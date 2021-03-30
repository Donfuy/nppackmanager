from tkinter import ttk, filedialog, StringVar, Tk, Listbox, messagebox
from tkinter import N, W, E, S, HORIZONTAL, FALSE
from setup import Setup
from manager import *
from definitions import *
from os import path
import configparser
import asyncio
import threading


class SetupWindow(ttk.Frame):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.content = ttk.Frame(root, padding=(5, 5, 5, 5))
        self.content.grid(column=0, row=0, sticky=(N, W, E, S))
        self.logic = Setup()
        self.asyncio_loop = asyncio.get_event_loop()

        ######
        # USER NPP
        #
        self.user_npp_lframe = ttk.Labelframe(self.content, text='N++ User Folder', padding=(10, 10, 10, 10))
        self.user_npp_lframe.grid_rowconfigure(1, weight=1)
        self.user_npp_lframe.grid_rowconfigure(0, weight=1)
        self.user_npp_lframe.grid_columnconfigure(0, weight=0)
        self.user_npp_lframe.grid_columnconfigure(1, weight=1)
        self.user_npp_lframe.grid_columnconfigure(2, weight=1)
        self.user_npp_lframe.grid_columnconfigure(3, weight=5)

        self.user_npp_description = ttk.Label(self.user_npp_lframe, text=USER_NPP_DESCRIPTION)
        self.user_npp_locate_btn = ttk.Button(self.user_npp_lframe, text='Set', command=self.on_locate_user_npp_btn)
        self.user_npp_location = StringVar()
        self.user_npp_location.set(NOT_SET)
        self.user_npp_location_label = ttk.Label(self.user_npp_lframe, textvariable=self.user_npp_location)

        self.user_npp_locate_btn.grid(column=0, columnspan=1, row=1, sticky=W)
        self.user_npp_description.grid(column=0, columnspan=3, row=0, sticky=(N, W))
        self.user_npp_location_label.grid(column=1, columnspan=2, row=1, sticky=W)

        ######
        # NPP
        #
        self.npp_lframe = ttk.Labelframe(self.content, text='N++ Steam/Kartridge Folder', padding=(10, 10, 10, 10))
        self.npp_lframe.grid_rowconfigure(1, weight=1)
        self.npp_lframe.grid_rowconfigure(0, weight=1)
        self.npp_lframe.grid_columnconfigure(0, weight=0)
        self.npp_lframe.grid_columnconfigure(1, weight=1)
        self.npp_lframe.grid_columnconfigure(2, weight=1)
        self.npp_lframe.grid_columnconfigure(3, weight=5)

        self.npp_description = ttk.Label(self.npp_lframe, text=NPP_DESCRIPTION)
        self.npp_locate_btn = ttk.Button(self.npp_lframe, text='Set', command=self.on_locate_npp_btn)

        self.npp_location = StringVar()
        self.npp_location.set(NOT_SET)
        self.npp_location_label = ttk.Label(self.npp_lframe, textvariable=self.npp_location)

        self.npp_description.grid(column=0, columnspan=3, row=0, sticky=(N, W))
        self.npp_locate_btn.grid(column=0, columnspan=1, row=1, sticky=W)
        self.npp_location_label.grid(column=1, columnspan=2, row=1, sticky=W)

        ######
        # CONTROLS
        #
        self.start_btn = ttk.Button(self.content, text='Start N++ Manager', command=self.on_start_btn)
        self.reset_btn = ttk.Button(self.content, text='Reset')

        ######
        # PROGRESS
        #
        self.progress = ttk.Progressbar(self.content, orient=HORIZONTAL, length=6, mode='determinate')
        self.progress_description = ttk.Label(self.content, text='Setting up N++ Manager...')

        ######
        # WINDOW GRID
        #
        self.user_npp_lframe.grid(column=0, columnspan=2, row=0, sticky=(N, W, E))
        self.npp_lframe.grid(column=0, columnspan=2, row=1, sticky=(S, W, E))
        self.start_btn.grid(column=1, row=2, sticky=(S, E))

    def on_locate_npp_btn(self):
        npp_folder = filedialog.askdirectory()
        if npp_folder == '':
            self.npp_location.set(NOT_SET)
        else:
            # TODO: Verify npp_folder
            self.logic.npp = npp_folder
            self.npp_location.set(self.logic.npp)

    def on_locate_user_npp_btn(self):
        user_npp_folder = filedialog.askdirectory()
        if user_npp_folder == '':
            self.user_npp_location.set(NOT_SET)
        # TODO: Verify user_npp_folder
        self.logic.user_npp = user_npp_folder
        self.user_npp_location.set(self.logic.user_npp)

    def on_reset_btn(self):
        return None

    def on_start_btn(self):
        self.do_setup()

    def do_setup(self):
        threading.Thread(target=self._asyncio_thread(), args=(asyncio_loop,)).start()

    def _asyncio_thread(self):
        self.start_btn.grid_remove()
        self.progress.grid(column=0, columnspan=2, row=3, sticky=(N, E, W, S))
        self.progress_description.grid(column=0, columnspan=2, row=2, sticky=(N, E, W, S))
        self.progress_description['text'] = 'Creating config file'
        self.progress['value'] = 10
        self.update()
        asyncio_loop.run_until_complete(self.logic.create_config_file())

        self.progress_description['text'] = 'Packs folder'
        self.progress['value'] = 20
        self.update()
        asyncio_loop.run_until_complete(self.logic.create_packs_folder())

        self.progress_description['text'] = 'Selected'
        self.progress['value'] = 30
        self.update()
        asyncio_loop.run_until_complete(self.logic.create_selected_file())

        self.progress_description['text'] = 'Zipping nprofiles'
        self.progress['value'] = 40
        self.update()
        asyncio_loop.run_until_complete(self.logic.zip_metanet_nprofiles())

        self.progress_description['text'] = 'Packin attracts'
        self.progress['value'] = 60
        self.update()
        asyncio_loop.run_until_complete(self.logic.copy_metanet_attracts())

        self.progress_description['text'] = 'Metanet packin'
        self.progress['value'] = 80
        self.update()
        asyncio_loop.run_until_complete(self.logic.generate_metanet_pack())

        self.progress_description['text'] = 'Done!'
        self.progress['value'] = 100
        # TODO: and then start the manager window


class ManagerWindow(ttk.Frame):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.content = ttk.Frame(root, padding=(5, 5, 5, 5))
        self.content.grid(column=0, row=0, sticky=(N, W, E, S))
        self.content.grid_rowconfigure(0, weight=0)
        self.content.grid_columnconfigure(0, weight=0)
        self.content.grid_columnconfigure(1, weight=5)

        ######
        # PACKS
        #
        self.packs_lframe = ttk.Labelframe(self.content, text='Packs', padding=(10, 10, 10, 10))

        self.packs = StringVar()
        self.packs_lbox = Listbox(self.packs_lframe, listvariable=self.packs, selectmode='browse')

        self.packs_lbox.grid(column=0, row=0, columnspan=2, sticky=(N, E, W, S))

        self.load_btn = ttk.Button(self.packs_lframe, text='Load', command=self.on_load_btn_click)
        self.load_btn.grid(column=2, row=0, padx=10, sticky=(N, E, W))

        self.add_btn = ttk.Button(self.packs_lframe, text='Add', command=self.on_add_btn_click)
        self.add_btn.grid(column=0, row=1, pady=10, sticky=W)

        self.remove_btn = ttk.Button(self.packs_lframe, text='Remove', command=self.on_remove_btn_click)
        self.remove_btn.grid(column=1, row=1, pady=10, sticky=W)

        self.active_pack_description_lframe = ttk.LabelFrame(self.content, text='Active pack', padding=(10, 10, 10, 10))
        self.active_pack = StringVar()
        self.active_pack_label = ttk.Label(self.active_pack_description_lframe, textvariable=self.active_pack)

        ######
        # WINDOW GRID
        #
        self.active_pack_description_lframe.grid(column=0, columnspan=2, row=0, sticky=(N, E, W, S))
        self.active_pack_label.grid(column=0, row=0, sticky=(N,W))
        self.packs_lframe.grid(column=0, columnspan=2, row=1, sticky=(N, E, W, S))
        self.packs.set(get_pack_list())
        self.active_pack.set(get_selected())

    def on_add_btn_click(self):
        file = filedialog.askopenfilename()
        if not file == '':
            filename = path.basename(file)
            pack_name = filename[:-len(EXT_NPPACK)]
            if not filename[-len(EXT_NPPACK):] == EXT_NPPACK:
                # TODO: NOT A NPPACK DIALOG
                print('wow:', filename[:-len(EXT_NPPACK)])
                print(filename)
                print(len(EXT_NPPACK))

            if pack_exists(pack_name):
                if messagebox.askyesno(
                        message='Pack ' + pack_name + ' already exists. Do you want to replace it?\n THIS WILL ERASE ALL PROGRESS FROM THIS PACK.'):
                    remove_pack(pack_name)
            add_pack(file)
            self.packs.set(get_pack_list())

    def on_load_btn_click(self):
        selection_id = self.packs_lbox.curselection()
        load_pack(self.packs_lbox.get(selection_id))
        self.active_pack.set(get_selected())
        print(get_selected())

    def on_remove_btn_click(self):
        selection_id = self.packs_lbox.curselection()
        if not self.packs_lbox.get(selection_id) == METANET:
            remove_pack(self.packs_lbox.get(selection_id))
        self.packs.set(get_pack_list())
        self.active_pack.set(get_selected())


def setup():
    app = Tk()
    app.title("N++ Pack Manager Setup")
    app.resizable(FALSE, FALSE)
    handle = app
    SetupWindow(app)
    app.mainloop()


def manager():
    app = Tk()
    app.title("N++ Pack Manager")
    app.resizable(FALSE, FALSE)
    ManagerWindow(app)
    app.mainloop()


def verify_setup():
    if path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        user_npp = config[SECTION_LOC][KEY_USER_NPP_LOC]
        bin_npp = config[SECTION_LOC][KEY_NPP_LOC]
        folder_packs = path.join(user_npp, PACKS)
        if not path.isdir(user_npp):
            return False
        elif not path.isdir(bin_npp):
            return False
        elif not path.isdir(folder_packs):
            return False
        return True


if __name__ == '__main__':
    asyncio_loop = asyncio.get_event_loop()
    handle = None
    if verify_setup():
        manager()
    else:
        setup()
        if verify_setup():
            manager()
