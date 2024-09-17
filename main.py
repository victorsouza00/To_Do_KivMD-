import locale
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.utils import platform
from kivy.core.window import Window

from datetime import datetime


if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


from database import Database

# Initialize db instance
db = Database()


class DialogContent(MDBoxLayout):
    """Abre a caixa de dialogo das tasks"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        self.ids.date_text.text = str(datetime.now().strftime('%A, %d de %B de %Y'))
        """Vai mostrar a data nesse exato momento"""

    
    def show_date_picker(self):
        """Opens the date picker"""
        date_dialog = MDDatePicker()##Armazenando em uma variavel , Widget do KivyMD
        date_dialog.bind(on_save=self.on_save)##O metodo on save vai pegar a data e armazenar com uma leitura mais facil
        date_dialog.open()##Metodo padrão que vai abrir 

    def on_save(self, instance, value, date_range):
        """This functions gets the date from the date picker and converts its it a
        more friendly form then changes the date label on the dialog to that"""

        date = value.strftime('%A, %d de %B de %Y')
        self.ids.date_text.text = str(date)


class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk


    def mark(self, check, the_list_item):
        '''mark the task as complete or incomplete'''
        if check.active == True:
            the_list_item.text = '[s]'+the_list_item.text+'[/s]'
            db.mark_task_as_complete(the_list_item.pk)# here
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))# Here

    def delete_item(self, the_list_item):
        '''Delete the task'''
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)# Here



class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''



class MainApp(MDApp):
    task_list_dialog = None

    """Dark mode"""
    def Dark_Mode_Btn(self):
        if self.theme_cls.primary_palette == "Orange":
            Window.clearcolor = (1, 1, 1, 1)  
            self.theme_cls.primary_palette = "Blue"
            primary_text_color = (0, 0, 0, 1)  
            secondary_text_color = (0.3, 0.3, 0.3, 1)  
            checkbox_color = (0, 0, 0, 1)  #
        else:
            Window.clearcolor = (0.1, 0.1, 0.1, 1) 
            self.theme_cls.primary_palette = "Orange"
            primary_text_color = (200/255, 200/255, 200/255, 1)  
            secondary_text_color = (150/255, 150/255, 150/255, 1)  
            checkbox_color = (200/255, 200/255, 200/255, 1)  

        # Atualiza a cor do texto do task_label
        self.root.ids.task_label.theme_text_color = "Custom"
        self.root.ids.task_label.text_color = primary_text_color

        # Muda a cor dos itens da lista 
        for task_item in self.root.ids.container.children:
            task_item.ids._lbl_primary.theme_text_color = "Custom"
            task_item.ids._lbl_primary.text_color = primary_text_color
            
            task_item.ids._lbl_secondary.theme_text_color = "Custom"
            task_item.ids._lbl_secondary.text_color = secondary_text_color
            
            task_item.ids.check.color = checkbox_color  # Define a cor do checkbox

    def show_deleted_tasks(self):
        """Mostra as atividades deletadas"""
        deleted_tasks = db.get_deleted_tasks()
        self.root.ids.container.clear_widgets()  # Limpar a lista atual

        for task in deleted_tasks:
            add_task = ListItemWithCheckbox(pk=task[0], text='[s]'+task[1]+'[/s]', secondary_text=f'{task[2]} - Deletado as   {task[3]}')
            self.root.ids.container.add_widget(add_task)

    
    def show_main_tasks(self):
        """Mostra as atividades principais"""
        completed_tasks, uncomplete_tasks = db.get_tasks()
        self.root.ids.container.clear_widgets()  # Limpar a lista atual

        # Definir cores baseado no tema atual
        if self.theme_cls.primary_palette == "Blue":
            primary_text_color = (0, 0, 0, 1)
            secondary_text_color = (0.3, 0.3, 0.3, 1)
            checkbox_color = (0, 0, 0, 1)
        else:
            primary_text_color = (200/255, 200/255, 200/255, 1)
            secondary_text_color = (150/255, 150/255, 150/255, 1)
            checkbox_color = (200/255, 200/255, 200/255, 1)

        # Mostrar tarefas incompletas
        if uncomplete_tasks:
            for task in uncomplete_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2])
                add_task.ids._lbl_primary.theme_text_color = "Custom"
                add_task.ids._lbl_primary.text_color = primary_text_color
                add_task.ids._lbl_secondary.theme_text_color = "Custom"
                add_task.ids._lbl_secondary.text_color = secondary_text_color
                add_task.ids.check.color = checkbox_color
                self.root.ids.container.add_widget(add_task)

        # Mostrar tarefas completas
        if completed_tasks:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text='[s]'+task[1]+'[/s]', secondary_text=task[2])
                add_task.ids._lbl_primary.theme_text_color = "Custom"
                add_task.ids._lbl_primary.text_color = primary_text_color
                add_task.ids._lbl_secondary.theme_text_color = "Custom"
                add_task.ids._lbl_secondary.text_color = secondary_text_color
                add_task.ids.check.color = checkbox_color
                add_task.ids.check.active = True
                self.root.ids.container.add_widget(add_task)


    

    def build(self):
        # Setting theme to my favorite theme
        self.theme_cls.primary_palette = "Blue"

    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Adicione uma Tarefa",
                type="custom",
                content_cls=DialogContent(),
            )

        self.task_list_dialog.open()

    def on_start(self):
        
        try:
            completed_tasks, uncomplete_tasks = db.get_tasks()

            # Determina a cor do texto das tarefas baseado no tema atual
            if self.theme_cls.primary_palette == "Blue":
                primary_text_color = (0, 0, 0, 1)
                secondary_text_color = (0.3, 0.3, 0.3, 1)
                checkbox_color = (0, 0, 0, 1)
            else:
                primary_text_color = (200/255, 200/255, 200/255, 1)
                secondary_text_color = (150/255, 150/255, 150/255, 1)
                checkbox_color = (200/255, 200/255, 200/255, 1)
            if uncomplete_tasks != []:
                for task in uncomplete_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2])
                    add_task.ids._lbl_primary.theme_text_color = "Custom"
                    add_task.ids._lbl_primary.text_color = primary_text_color
                    add_task.ids._lbl_secondary.theme_text_color = "Custom"
                    add_task.ids._lbl_secondary.text_color = secondary_text_color
                    add_task.ids.check.color = checkbox_color
                    self.root.ids.container.add_widget(add_task)

            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text='[s]'+task[1]+'[/s]', secondary_text=task[2])
                    add_task.ids._lbl_primary.theme_text_color = "Custom"
                    add_task.ids._lbl_primary.text_color = primary_text_color
                    add_task.ids._lbl_secondary.theme_text_color = "Custom"
                    add_task.ids._lbl_secondary.text_color = secondary_text_color
                    add_task.ids.check.color = checkbox_color
                    add_task.ids.check.active = True
                    self.root.ids.container.add_widget(add_task)
        except Exception as e:
            print(e)
            pass

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_date):
        '''Add task to the list of tasks'''

        # Add task to the db
        created_task = db.create_task(task.text, task_date)# Here

        # return the created task details and create a list item
        self.root.ids['container'].add_widget(ListItemWithCheckbox(pk=created_task[0], text='[b]'+created_task[1]+'[/b]', secondary_text=created_task[2]))# Here
        task.text = ''

if __name__ == '__main__':
    app = MainApp()
    app.run()