import sqlite3

class Database:
    
    def __init__(self):
        self.con = sqlite3.connect('todo.db')
        self.cursor = self.con.cursor()
        self.create_task_table()
        self.create_deleted_tasks_table()
    
    
    

    def create_task_table(self):
        """Create tasks table"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varchar(50) NOT NULL, due_date varchar(50), completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")
        self.con.commit()
        

    def create_task(self, task, due_date=None):
        """Create a task"""
        self.cursor.execute("INSERT INTO tasks(task, due_date, completed) VALUES(?, ?, ?)", (task, due_date, 0))
        self.con.commit()

        # GETTING THE LAST ENTERED ITEM SO WE CAN ADD IT TO THE TASK LIST
        created_task = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE task = ? and completed = 0", (task,)).fetchall()
        return created_task[-1]

    def get_tasks(self):
        """Get tasks"""
        uncomplete_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed = 0").fetchall()
        completed_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed = 1").fetchall()

        return completed_tasks, uncomplete_tasks

    

    def mark_task_as_complete(self, taskid):
        """Marking tasks as complete"""
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (taskid,))
        self.con.commit()

    def mark_task_as_incomplete(self, taskid):
        """Mark task as uncomplete"""
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (taskid,))
        self.con.commit()

        # return the text of the task
        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (taskid,)).fetchall()
        return task_text[0][0]

    def delete_task(self, taskid):
        task_to_delete = self.cursor.execute("SELECT * FROM tasks WHERE id=?", (taskid,)).fetchone()
        self.cursor.execute("INSERT INTO deleted_tasks(id, task, due_date) VALUES(?, ?, ?)", (task_to_delete[0], task_to_delete[1], task_to_delete[2]))
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (taskid,))

   

    def create_deleted_tasks_table(self):
        """Create deleted tasks table"""
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS deleted_tasks(id integer PRIMARY KEY AUTOINCREMENT, task varchar(50) NOT NULL, due_date varchar(50), deleted_at timestamp DEFAULT CURRENT_TIMESTAMP)"
        )
        self.con.commit()
    
    def get_deleted_tasks(self):
        """Retrieve deleted tasks"""
        return self.cursor.execute("SELECT id, task, due_date, deleted_at FROM deleted_tasks").fetchall()
    
    
    def close_db_connection(self):
            self.con.close()
        