from definitions import *
from configparser import ConfigParser
from os import path, mkdir, listdir
from shutil import make_archive, rmtree, copytree, copy


# TODO: Handle errors like file existing or no access (through dialogs or somethin)
# TODO: Handle IO errors generally
class Setup:
    def __init__(self):
        self.npp = ''
        self.user_npp = ''
        self.progress_bar = None
        self.progress_bar_description = None

    async def create_config_file(self):
        config = ConfigParser()
        config[SECTION_LOC] = {KEY_NPP_LOC: self.npp,
                               KEY_USER_NPP_LOC: self.user_npp}

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    # TODO: Handle errors
    async def create_packs_folder(self):
        packs_loc = path.join(self.user_npp, PACKS)
        mkdir(packs_loc)

    async def create_selected_file(self):
        selected_file_path = path.join(self.user_npp, PACKS, SELECTED_FILE)
        with open(selected_file_path, 'w') as selected:
            selected.write(METANET)

    async def zip_metanet_nprofiles(self):
        copytree(path.join('res', METANET), path.join('res', METANET_COPY))
        user_nprofile_loc = path.join(self.user_npp, NPROFILE)
        user_nprofile_old_loc = path.join(self.user_npp, NPROFILE_OLD)
        temp_folder = path.join('res', METANET_COPY, 'nprofiles')
        copy(user_nprofile_loc, path.join(temp_folder, NPROFILE))
        copy(user_nprofile_old_loc, path.join(temp_folder, NPROFILE_OLD))
        make_archive(temp_folder, 'zip', root_dir=temp_folder)
        rmtree(temp_folder)

    async def copy_metanet_attracts(self):
        user_attract_loc = path.join(self.user_npp, ATTRACT)
        for file in listdir(user_attract_loc):
            copy(path.join(user_attract_loc, file), path.join('res', METANET_COPY, 'attract', file))

    async def generate_metanet_pack(self):
        copytree(path.join('res', METANET_COPY), path.join(self.user_npp, PACKS, METANET))
        # make_archive(METANET, 'zip', root_dir=path.join('res', METANET_COPY))
        # copy(METANET + EXT_ZIP, path.join(self.user_npp, PACKS, METANET + EXT_NPPACK))
        # remove(METANET + EXT_ZIP)
        rmtree(path.join('res', METANET_COPY))
