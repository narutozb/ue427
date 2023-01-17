import csv
import os
import unreal


class CustomInformation:
    __ALL_INFORMATION = {}

    SKELETAL_MESH_LIST = []
    SKELETAL_MESH_LIST_FIELDS = []
    #
    TEXTURE2D_LIST = []
    TEXTURE2D_LIST_FIELDS = []

    def __init__(self):
        pass

    @classmethod
    def clear_all_information(cls):
        cls.SKELETAL_MESH_LIST = []
        cls.SKELETAL_MESH_LIST_FIELDS = []
        cls.TEXTURE2D_LIST = []
        cls.TEXTURE2D_LIST_FIELDS = []

    @classmethod
    def get_csv_fields(cls, l: list):
        if len(l) > 0:
            return list(l[0].keys())
        return []

    @staticmethod
    def get_base_information(base_object: unreal.Object):
        return {
            'Name': base_object.get_name(),
            'FullName': base_object.get_full_name(),
            'PathName': base_object.get_path_name()
        }

    @staticmethod
    def append_information_to_list(data: dict, l: list) -> None:
        l.append(data)

    @classmethod
    def get_skeletal_mesh_information(cls):
        return cls.SKELETAL_MESH_LIST

    @classmethod
    def get_texture2d_information(cls):
        return cls.TEXTURE2D_LIST

    @classmethod
    def get_full_string_dict(cls, l=[]):
        full_string_list = []
        for d in l:
            new_d = {}
            for k, v in d.items():
                if isinstance(v, list):
                    new_d[k] = '\n'.join(v)
                else:
                    new_d[k] = v
            full_string_list.append(new_d)
        return full_string_list

    @staticmethod
    def merge_two_dict(d1: dict, d2: dict):
        return {**d1, **d2}

    @classmethod
    def write_to_csv(cls, needed_information: dict = None, csv_path=None):
        """

        :param needed_information:
        :param csv_path:
        :return:
        """
        if not needed_information:
            needed_information = {
                'SkeletalMesh': cls.get_skeletal_mesh_information(),
                'Texture2D': cls.get_texture2d_information(),
            }

        for k, v in needed_information.items():
            info = v
            type_name = k

            infos = cls.get_full_string_dict(info)
            field_names = cls.get_csv_fields(infos)
            # csv file 's path
            csv_path = os.path.join(os.path.expanduser('~'), f'_ue_assets_information_{type_name}.csv')

            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(infos)


class CustomSkeletalMesh(CustomInformation):

    def __init__(self, skeletal_mesh: unreal.SkeletalMesh = unreal.SkeletalMesh):
        super().__init__()
        self.skeletal_mesh = skeletal_mesh
        self.skeletal_mesh_full_name = self.skeletal_mesh.get_full_name()

        self.append_to_skeletal_mesh_information()

    def get_source_file(self):
        return self.skeletal_mesh.get_editor_property('asset_import_data').get_first_filename()

    def get_materials_slot_name(self):
        return [i.material_slot_name.__str__() for i in self.skeletal_mesh.materials]

    def get_materials_interface(self):
        res = []
        for i in self.skeletal_mesh.materials:
            if i.material_interface:
                res.append(i.material_interface.get_name())
            else:
                res.append('None')
        return res

    def get_materials_base_material(self):
        res = []
        for i in self.skeletal_mesh.materials:
            if i.material_interface:
                res.append(i.material_interface.get_base_material().get_name())
            else:
                res.append('None')

        return res
        # return [i.material_interface.get_base_material().get_name().__str__() for i in self.skeletal_mesh.materials if
        #         i.material_interface is not None]

    def is_source_file_same(self, custom_skeletal_mesh):
        """

        :param custom_skeletal_mesh: CustomSK
        :return:
        """
        if self.get_source_file() == custom_skeletal_mesh.get_source_file():
            return True

    def get_morph_targets_name(self):
        return [i.get_name() for i in self.skeletal_mesh.morph_targets]

    def get_skeleton_name(self):
        return self.skeletal_mesh.skeleton.get_name()

    def append_to_skeletal_mesh_information(self):
        res = {
            'MaterialSlotName': self.get_materials_slot_name(),
            'MaterialBaseMaterial': self.get_materials_base_material(),
            'MaterialInterface': self.get_materials_interface(),
            'SourceFileName': self.get_source_file(),
            'MorphTargetNames': self.get_morph_targets_name(),
            'SkeletonName': self.get_skeleton_name(),

        }
        self.append_information_to_list(
            self.merge_two_dict(
                self.get_base_information(self.skeletal_mesh), res),
            self.SKELETAL_MESH_LIST
        )


class CustomTexture2D(CustomInformation):
    def __init__(self, texture: unreal.Texture2D):
        super().__init__()
        self.texture2d = texture
        self.append_to_texture_2d_information()

    def append_to_texture_2d_information(self):
        res = {
            'SourceFileName': self.texture2d.get_editor_property('asset_import_data').get_first_filename(),
        }
        self.append_information_to_list(
            self.merge_two_dict(
                self.get_base_information(self.texture2d), res
            ),
            self.TEXTURE2D_LIST
        )


def main():
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    CustomInformation.clear_all_information()
    for i in selected_assets:
        if isinstance(i, unreal.SkeletalMesh):
            CustomSkeletalMesh(i)
        elif isinstance(i, unreal.Texture2D):
            CustomTexture2D(i)

    # output csv
    CustomInformation.write_to_csv()


if __name__ == '__main__':
    main()
