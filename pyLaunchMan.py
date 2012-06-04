import curses
import sqlite3
import os
from glob import glob

COL2_START = 38

database_file = ''
screen = None
apps = []
apps_selected = []
page = 1

def main_menu():
    screen.clear()
    size = screen.getmaxyx()
    screen.addstr(size[0]-1, 0, " pyLaunchMan", curses.A_REVERSE)
    screen.addstr(" | (n)ext", curses.A_REVERSE)
    screen.addstr(" | (p)rev", curses.A_REVERSE)
    screen.addstr(" | (r)ename apps", curses.A_REVERSE)
    screen.addstr(" | (d)elete apps", curses.A_REVERSE)
    screen.addstr(" | (q)uit", curses.A_REVERSE)
    
    screen.insnstr("                                                                                ", 80, curses.A_REVERSE)


def load_apps_page():
    global apps
    global page
    main_menu()
    screen.addstr(1, 1, "Launchpad Database: %s\n" % os.path.split(database_file)[1])
    db_conn = sqlite3.connect(database_file)
    try:
        cursor = db_conn.cursor()
    
        cursor.execute("""SELECT item_id, title 
                          FROM groups
                          ORDER BY item_id""")
        groups = cursor.fetchall()
        
        if page+1 > (len(groups)-1):
            page -= 1
            
        p = groups[page+1][0]
        
        if  groups[page+1][1]:
            screen.addstr("                        -- Folder %s --\n" % groups[page+1][1])
        else:
            screen.addstr("                              -- Page %s --\n" % page)
        
        cursor.execute("""SELECT rowid, a.title, ordering, g.title as folder
                          FROM items i 
                          LEFT JOIN apps a ON a.item_id=i.rowid 
                          LEFT JOIN groups g ON g.item_id=i.rowid
                          WHERE i.parent_id=?
                          ORDER BY ordering""", (p,))
                          
        apps = cursor.fetchall()
    except:
        screen.addstr("There was an error accessing the database\n")
        curses.endwin()
    finally:
        cursor.close()
        db_conn.close()    
    
    list_apps()
    
    
def list_apps():
    global apps_selected
    apps_selected[:] = []

    max_items = 40 # full screen of apps
    if max_items > len(apps): max_items = len(apps)
    
    print len(apps)
    
    for i in range(0, max_items, 2):
        title = apps[i][1]
        if not title:
            title = '+ '+apps[i][3]
        screen.addstr(" [ ] %s" % title)
            
        if i+1 < len(apps):
            title = apps[i+1][1]
            if not title:
                title = '+ '+apps[i+1][3]
            screen.addstr(screen.getyx()[0], COL2_START-1, "[ ] %s\n" % title)
        
    screen.move(3, 2)
    
            
def toggle_selected():
    global apps_selected
    cur = screen.getyx()
    i = (cur[0] - 3) * 2
    if cur[1] == COL2_START:
        i = i + 1
        
    ch = ord('x')
    if apps_selected.count(i):
        apps_selected.remove(i)
        ch = ord(' ')
    else:    
        apps_selected.append(i)
        
    screen.addch(ch)
    screen.move(cur[0], cur[1])
    
    
def delete_selected():
    size = screen.getmaxyx()
    screen.addstr(size[0]-2, 4, "delete selected apps? (y)es / (n)o ")
    while True:
        event = screen.getch()
        if event == ord('y'):
            global apps_selected
            for a in apps_selected:
                delete_app(apps[a][0])
                
            apps_selected[:] = []
            load_apps_page()
            return True
        else:
            screen.move(size[0]-2, 0)
            screen.clrtoeol()
            screen.move(3, 2)
            return False
             
    
def delete_app(item_id):
    db_conn = sqlite3.connect(database_file)
    try:
        cursor = db_conn.cursor()
        
        #check to see if app is a folder
        cursor.execute("""SELECT rowid FROM groups WHERE rowid=?""", (item_id,))
        item = cursor.fetchone()
        if item:
            #item is a folder
            cursor.execute("""SELECT rowid FROM items WHERE parent_id=?""", (item[0],))
            items = cursor.fetchall()
            for i in items:
                cursor.execute("""DELETE FROM apps WHERE item_id=?""", (i[0],))
                cursor.execute("""DELETE FROM items WHERE rowid=?""", (i[0],))
                
            cursor.execute("""DELETE FROM groups WHERE rowid=?""", (item[0],))
    
        cursor.execute("""DELETE FROM apps WHERE item_id=?""", (item_id,))
        cursor.execute("""DELETE FROM items WHERE rowid=?""", (item_id,))
        
        db_conn.commit()
        
        #Check to see if deletions leave an empty page
        cursor.execute("""SELECT g.rowid, count(i.rowid) 
                          FROM groups g 
                          LEFT JOIN items i ON i.parent_id=g.rowid 
                          WHERE g.title is null 
                          AND g.rowid>2 
                          GROUP BY g.rowid""")
        groups = cursor.fetchall()
        for g in groups:
            if g[1] == 0:
                cursor.execute("""DELETE FROM groups WHERE rowid=?""", (g[0],))
        db_conn.commit()
        
        
    except:
        curses.endwin()
    finally:
        cursor.close()
        db_conn.close()
    
    
def rename_selected():
    global apps_selected
    global apps
    size = screen.getmaxyx()
    curses.echo()
    
    db_conn = sqlite3.connect(database_file)
    try:
        cursor = db_conn.cursor()
        
        for a in apps_selected:
            screen.addstr(size[0]-2, 4, "Rename %s to: " % apps[a][1])
            screen.clrtoeol()
            name = screen.getstr(size[0]-2, 16+len(apps[a][1]), 25)
            cursor.execute("""UPDATE apps SET title=? WHERE item_id=?""", (name, apps[a][0]))

        db_conn.commit()
    except:
        print "error with database"
        curses.endwin()
        raise
    finally:
        cursor.close()
        db_conn.close()
        
    curses.noecho()
    apps_selected[:] = []
    load_apps_page()


    
def next_page():
    global page
    page += 1
    
    load_apps_page()
    
def prev_page():
    global page
    page -= 1
    
    if page < 1:
        page = 1
        
    load_apps_page()
    
    
def scan_db():
    screen.clear()
    screen.addstr(1, 1, "Scanning Database: %s\n" % database_file)
    db_conn = sqlite3.connect(database_file)
    try:
        cursor = db_conn.cursor()
        
        cursor.execute("""SELECT rowid, a.title, ordering, g.title as folder, g.item_id as gid
                          FROM items i 
                          LEFT JOIN apps a ON a.item_id=i.rowid 
                          LEFT JOIN groups g ON g.item_id=i.rowid
                          WHERE i.rowid > 2
                          ORDER BY ordering""")
                          
        apps = cursor.fetchall()
        
        cursor.close()
        db_conn.close()
        
        print apps
        
        appless_items = []
        
        for a in apps:
            if not a[1] and not a[3] and not a[4]:
                appless_items.append(a[0])
               
        for d in appless_items:
            delete_app(d)
        
    except:
        curses.endwin()
    finally:
        db_conn.close()    
    

def cursor_down():
    cur = screen.getyx()
    if cur[0] < (len(apps) / 2) + 2 + (len(apps) % 2):
        screen.move(cur[0]+1, cur[1])
        
def cursor_up():
    cur = screen.getyx()
    if cur[0] > 3:
        screen.move(cur[0]-1, cur[1])
        
def cursor_right():
    cur = screen.getyx()
    if cur[1] != COL2_START:
        screen.move(cur[0], COL2_START)
    
        
def cursor_left():
    cur = screen.getyx()
    if cur[1] != 2:
        screen.move(cur[0], 2)
        

if __name__ == '__main__':

    files = glob(os.path.expanduser('~/Library/Application Support/Dock/*.db'))
    if len(files) < 1:
        print "Error: can't find LaunchPad Database file :("
        exit()
        
    database_file = files[0]

    try:
        screen = curses.initscr()
        curses.noecho()
        screen.keypad(1)
    
    except:
        curses.endwin()
        
    screen.addstr(1, 1, "WARNING: pyLaunchMan is about to scan your database file for orphaned items.\n")
    screen.addstr("  This will make changes to your LaunchPad database file\n")
    screen.addstr("  Are you SURE you want to contine? (y)es / (n)o ")
    
    while True:
        event = screen.getch()
        if event == ord('y'): break
        else:
            curses.endwin()
            print "Application quit without changing LaunchPad database file."
            exit()
        
    scan_db()
        
    load_apps_page()
        
    while True:
        event = screen.getch()
        if event == ord('q'): break
        elif event == ord(' '): toggle_selected()
        
        elif event == ord('r'): rename_selected()
        elif event == ord('d'): delete_selected()
        
        elif event == ord('n'): next_page()
        elif event == ord('p'): prev_page()
        
        elif event == curses.KEY_DOWN: cursor_down()
        elif event == curses.KEY_UP: cursor_up()
        elif event == curses.KEY_RIGHT: cursor_right()
        elif event == curses.KEY_LEFT: cursor_left()
        
        
    screen.clear()    
    curses.endwin()
    
    print "Remember to restart the Dock: killall Dock"

    

