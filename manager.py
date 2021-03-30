from configparser import ConfigParser
from os import listdir, path, mkdir, remove
from shutil import unpack_archive, rmtree, copy, make_archive

from definitions import *


def get_packs_path():
    return path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], PACKS)


def get_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    return config


def get_pack_list():
    pack_list = []
    for pack in listdir(get_packs_path()):
        if path.isdir(path.join(get_packs_path(), pack)):
            pack_list.append(pack)
    return pack_list


def get_selected():
    selected_loc = path.join(get_packs_path(), SELECTED_FILE)
    with open(selected_loc, 'r') as sf:
        selected = sf.read()
        return selected


def set_selected(pack_name):
    selected_loc = path.join(get_packs_path(), SELECTED_FILE)
    with open(selected_loc, 'w') as sf:
        sf.write(pack_name)


def pack_exists(pack_name):
    for pack in get_pack_list():
        if pack == pack_name:
            return True
    return False


# TODO: verify_pack_integrity()
# TODO: if file is not .nppack
# TODO: if pack exists
def add_pack(adding_pack):
    pack_name = path.basename(adding_pack)[:-len(EXT_NPPACK)]
    mkdir(pack_name)
    extracted_pack_path = path.join(get_packs_path(), pack_name)
    unpack_archive(adding_pack, extracted_pack_path, 'zip')
    rmtree(pack_name)


def remove_pack(pack_name):
    if pack_name == get_selected():
        load_pack(METANET)
    rmtree(path.join(get_packs_path(), pack_name))


def unload_pack(pack_name):
    # Copy attracts to the stored pack and delete them from the user_npp folder
    attracts_folder = path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], ATTRACT)
    stored_pack_folder = path.join(get_packs_path(), pack_name)

    for attract in listdir(attracts_folder):
        stored_attract = path.join(stored_pack_folder, ATTRACT, attract)

        # Check if attract already exists in the stored pack
        if not path.isfile(stored_attract):
            copy(path.join(attracts_folder, attract), stored_attract)

        # Remove it from the user_npp folder
        remove(path.join(attracts_folder, attract))

    # Create nprofiles folder in packs
    mkdir(NPROFILES)

    # Copy nprofiles to the nprofiles folder
    user_nprofile = path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], NPROFILE)
    user_nprofile_old = path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], NPROFILE_OLD)
    copy(user_nprofile, path.join(NPROFILES, NPROFILE))
    copy(user_nprofile_old, path.join(NPROFILES, NPROFILE_OLD))

    # Remove nprofiles from the user folder
    remove(user_nprofile)
    remove(user_nprofile_old)

    # Delete nprofiles from the stored pack
    remove(path.join(stored_pack_folder, NPROFILES + EXT_ZIP))

    # Zip nprofiles and copy them over to the stored pack
    make_archive(path.join(stored_pack_folder, NPROFILES), 'zip', root_dir=NPROFILES)
    rmtree(NPROFILES)

    # Update selected
    set_selected(pack_name)

    # Delete levels from the npp folder
    rmtree(path.join(get_config()[SECTION_LOC][KEY_NPP_LOC], LEVELS))
    mkdir(path.join(get_config()[SECTION_LOC][KEY_NPP_LOC], LEVELS))


def load_pack(pack_name):
    # TODO: do checks on ui function
    unload_pack(get_selected())

    stored_pack_folder = path.join(get_packs_path(), pack_name)

    # TODO: check for no attracts
    if not path.isdir(path.join(stored_pack_folder, ATTRACT)):
        mkdir(path.join(stored_pack_folder, ATTRACT))
    # Copy attracts
    for attract in listdir(path.join(stored_pack_folder, ATTRACT)):
        attract_name = path.basename(attract)
        copy(path.join(stored_pack_folder, ATTRACT, attract), path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], ATTRACT, attract_name))

    # Copy levels
    for tab in listdir(path.join(stored_pack_folder, LEVELS)):
        tab_name = path.basename(tab)
        copy(path.join(stored_pack_folder, LEVELS, tab), path.join(get_config()[SECTION_LOC][KEY_NPP_LOC], LEVELS, tab_name))

    # Unzip and copy nprofiles
    mkdir(NPROFILES)
    unpack_archive(path.join(stored_pack_folder, NPROFILES + EXT_ZIP), NPROFILES)
    copy(path.join(NPROFILES, NPROFILE), path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], NPROFILE))
    copy(path.join(NPROFILES, NPROFILE_OLD), path.join(get_config()[SECTION_LOC][KEY_USER_NPP_LOC], NPROFILE_OLD))
    rmtree(NPROFILES)
    # Set selected
    set_selected(pack_name)
