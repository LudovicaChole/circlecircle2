import torch
import numpy as np
import json
import os
import torch.nn.functional as F


class TBox:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def update_device(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def map_ids(self, ids):
        """
        Enter any ID and convert it into a consecutive memory row number.

        :param ids: [3, 4, 8, 1, 3, 5]
        :return: mapping
        """

        ids_tensor = torch.as_tensor(ids, dtype=torch.long, device=self.device)

        max_id = ids_tensor.max().item()

        # Create a slightly larger container.
        mapping = torch.full([max_id + 1], -1, dtype=torch.long, device=self.device)

        # memory_row_number = index
        index = torch.arange(ids_tensor.shape[0], dtype=torch.long, device=self.device)

        # Use torch advanced search to map ids
        mapping[ids_tensor] = index

        return mapping, index

    def get_part_info(self, nodes, shells, part_name_mapping):
        """
        :param nodes: nodes
        :param shells: element_shell
        :param part_name_mapping: part_name_mapping
        :return: part_node_dict

        part_node_dict example: {
        "part_name":{
                    "ids": [nid1, nid2, nid3]
                    "coords": [[x, y, z], [x, y, z]]
                    "norms": [[normalized_x, normalized_y, normalized_z], [normalized_x, normalized_y, normalized_z]]
                    }
        }
        """

        part_info_dict = {}

        node_ids_tensor, node_coords_tensor, mapping_nodes, num_nodes, index_nodes = self._map_nids(nodes=nodes)

        eids_tensor, pids_tensor, enids_tensor, mapping_elements, num_elements, index_elements = self._map_eids(
            elements=shells)

        p = self._match_node_shell(mapping=mapping_nodes, coords=node_coords_tensor, element_nids=enids_tensor)

        element_normals, element_areas = self._calculate_shell_info(p=p)

        node_norms = self._calculate_node_info(nums=num_nodes,
                                               element_norms=element_normals,
                                               element_areas=element_areas,
                                               p=p)

        unique_pids = pids_tensor.unique()

        for pid in unique_pids:
            mask = pids_tensor == pid

            current_part_nids = enids_tensor[mask].unique()

            current_part_eids = eids_tensor[mask]

            current_node_index = mapping_nodes[current_part_nids]

            current_node_coords = node_coords_tensor[current_node_index]

            current_node_norms = node_norms[current_node_index]

            current_element_index = mapping_elements[current_part_eids]

            current_element_normal = element_normals[current_element_index]

            current_element_areas = element_areas[current_element_index]

            current_pid = pid.item()

            part_info_dict.setdefault(current_pid, {"node_ids": None,
                                                    "node_coords": None,
                                                    "node_norms": None,
                                                    "element_ids": None,
                                                    "element_norms": None,
                                                    "element_areas": None})

            part_info_dict[current_pid]["node_ids"] = current_part_nids

            part_info_dict[current_pid]["node_coords"] = F.normalize(current_node_coords, p=2, dim=1)

            part_info_dict[current_pid]["node_norms"] = current_node_norms

            part_info_dict[current_pid]["element_ids"] = current_part_eids

            part_info_dict[current_pid]["element_norms"] = current_element_normal

            part_info_dict[current_pid]["element_areas"] = current_element_areas

        recombined_part_info_dict = self._recombine_dictionary_by_name(source_dict=part_info_dict,
                                                                       part_name_mapping=part_name_mapping)

        return recombined_part_info_dict

    def concatenate_shell_solid_surfaces(self, elements_shell, solid_surfaces):
        """
        :param elements_shell: original shell
        :param solid_surfaces: solid surface elements
        :return: all_shell_element
        """
        elements_shell_tensor = torch.as_tensor(elements_shell, dtype=torch.int64, device=self.device)
        solid_surfaces_tensor = torch.as_tensor(solid_surfaces, dtype=torch.int64, device=self.device)

        unique_solid_surface_faces = self._unique_solid_surface(solid_surfaces=solid_surfaces_tensor)

        all_shell_element = torch.cat([elements_shell_tensor, unique_solid_surface_faces], dim=0)

        return all_shell_element

    def save(self, file_path, source_dict):
        """
        Function for saving files
        Must use "tensor_dict_to_list_dict" convert the tensor to a list when saving the file.

        :param file_path: original file path, like: .key file, .inp file ...
        :param source_dict: dictionary to save
        :return:
        """

        folder = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(basename)

        saved_file_path = os.path.join(folder, file_name + ".json")

        source_dict = self._tensor_dict_to_list_dict(source_dict=source_dict)

        with open(saved_file_path, mode="w", encoding="utf-8") as f:
            json.dump(source_dict, f, ensure_ascii=False, indent=4)

    # the following function only used internally
    def _map_nids(self, nodes):
        """
        Mapping the originally discrete node id to consecutive memory row numbers

        :param nodes: node list,
        :return: node_ids_tensor
        :return: node_coords_tensor
        :return: mapping: node id - memory row number, dictionary,
        :return: num_nodes: number of nodes, int

        nodes example: [[nid1, x, y, z],[nid2, x, y, z]]
        node_ids_tensor example: [nid1, nid2, nid3]
        node_coords_tensor example: [[x, y, z], [x, y, z]]
        mapping example: [-1,   -1,   -1,  ..., 4536, 4537, 4538]
        num_nodes example: 3
        """

        node_array = np.array(nodes, dtype=np.object_)

        node_ids = np.array(node_array[:, 0], dtype=np.int64)

        node_coords = np.array(node_array[:, 1:], dtype=np.float64)

        node_ids_tensor = torch.as_tensor(node_ids, dtype=torch.int64, device=self.device)

        node_coords_tensor = torch.as_tensor(node_coords, dtype=torch.float64, device=self.device)

        num_nodes = node_ids_tensor.shape[0]

        mapping, index = self.map_ids(ids=node_ids_tensor)

        return node_ids_tensor, node_coords_tensor, mapping, num_nodes, index

    def _map_eids(self, elements):
        """
        Mapping the originally discrete element id to consecutive memory row numbers

        :param elements:
        :return:
        """

        elements_tensor = torch.as_tensor(elements, dtype=torch.long, device=self.device)

        eids_tensor = elements_tensor[:, 0]

        pids_tensor = elements_tensor[:, 1]

        enids_tensor = elements_tensor[:, 2:]

        mapping, index = self.map_ids(ids=eids_tensor)

        num_elements = elements_tensor.shape[0]

        return eids_tensor, pids_tensor, enids_tensor, mapping, num_elements, index

    def _match_node_shell(self, mapping, coords, element_nids):
        """
        Match the coordinates of all nodes in the shell element

        :param mapping: node id - memory row number dictionary
        :param coords: node coords
        :param shells: element shell
        :return: (p1, p2, p3, p4, idx1, idx2, idx3, idx4, node_ids) = p

        mapping example: [-1,   -1,   -1,  ..., 4536, 4537, 4538]
        coords example: [[x, y, z],
                         [-779.3928182756, -442.3752121582, 335.28115568783],
                         [-779.3928182756, -452.3752121582, 325.28115568783],
                         [-779.3928182756, -432.3752121582, 345.28115568783]]
        elements example: [[eid, pid, n1, n2, n3, n4],
                           [18035299,  1800059, 18041256, 18041228, 18041229, 18041229],
                           [18035286,  1800059, 18039425, 18041229, 18041228, 18041236],
                           [18035301,  1800062, 18041293, 18041294, 18041281, 18041282]]
        """

        # element shell
        nidx1 = element_nids[:, 0]    # element_shell node id 1
        nidx2 = element_nids[:, 1]    # element_shell node id 2
        nidx3 = element_nids[:, 2]    # element_shell node id 3
        nidx4 = element_nids[:, 3]    # element_shell node id 4

        # idx: memory row number
        idx1 = mapping[nidx1]
        idx2 = mapping[nidx2]
        idx3 = mapping[nidx3]
        idx4 = mapping[nidx4]

        p1 = coords[idx1]    # node 1 coords: [x, y, z]
        p2 = coords[idx2]    # node 2 coords: [x, y, z]
        p3 = coords[idx3]    # node 3 coords: [x, y, z]
        p4 = coords[idx4]    # node 4 coords: [x, y, z]

        return p1, p2, p3, p4, idx1, idx2, idx3, idx4

    def _calculate_shell_info(self, p):
        """
        :param p: p
        :return: element_normal, element_areas

        p example: (p1, p2, p3, p4, idx1, idx2, idx3, idx4, node_ids), from match_node_coords_from_shell
        element_normal example: [[normalized_x, normalized_y, normalized_z],
                                 [-1.0000,  0.0000,  0.0000],
                                 [-1.0000, -0.0000,  0.0000],
                                 [ 0.7837,  0.3045,  0.5414]]
        element_areas example: [areas, 2.7737,  9.1843, 24.5275]
        element_ids example: [eid1, eid2, eid3]
        """

        p1, p2, p3, p4, idx1, idx2, idx3, idx4 = p

        v31 = p3 - p1    # diagonal 1 in shell
        v42 = p4 - p2    # diagonal 2 in shell

        element_normals = torch.linalg.cross(v31, v42)

        element_areas = 0.5 * torch.linalg.norm(element_normals, dim=1)

        element_normals = F.normalize(element_normals, p=2, dim=1)

        return element_normals, element_areas

    def _calculate_node_info(self, nums, element_norms, element_areas, p):
        """
        :param nums: node nums
        :param element_norms: element_normal
        :param element_areas: element_areas
        :param p: p
        :return: node_normal

        nums example: 3
        norms example: [[normalized_x, normalized_y, normalized_z],
                        [-1.0000,  0.0000,  0.0000],
                        [-1.0000, -0.0000,  0.0000],
                        [ 0.7837,  0.3045,  0.5414]] from calculate_shell_info
        areas example: [areas, 2.7737,  9.1843, 24.5275] from calculate_shell_info
        p example: (p1, p2, p3, p4, idx1, idx2, idx3, idx4), from match_node_coords_from_shell
        node_normal example: [[normalized_x, normalized_y, normalized_z],
                              [-1.0000,  0.0000,  0.0000],
                              [-1.0000, -0.0000,  0.0000]]
        """

        p1, p2, p3, p4, idx1, idx2, idx3, idx4 = p

        element_areas_2d = element_areas.unsqueeze(1)    # add dim [] to [[], []]

        weights_norms = element_norms * element_areas_2d    # element_norms * areas

        node_normals = torch.zeros((nums, 3), dtype=element_norms.dtype, device=self.device)    # placeholder

        node_normals.index_add_(dim=0, index=idx1, source=weights_norms)    # node 1 norm replace zeros with normal by index
        node_normals.index_add_(dim=0, index=idx2, source=weights_norms)    # node 2 norm replace zeros with normal by index
        node_normals.index_add_(dim=0, index=idx3, source=weights_norms)    # node 3 norm replace zeros with normal by index

        mask_s3_1d = (idx4 != idx3)    # check s3 element
        mask_s3_2d = mask_s3_1d.unsqueeze(1)    # add dim, [] to [[], []]

        # torch.where(condition, x, y), check node 4 normal, from s3 element and s4 element
        weights_norms_p4 = torch.where(mask_s3_2d, weights_norms, torch.zeros_like(weights_norms))

        node_normals.index_add_(dim=0, index=idx4, source=weights_norms_p4)    # node 4 norm replace zeros with normal

        # p=2 means Euclidean Distance
        node_normals = F.normalize(node_normals, p=2, dim=1)

        return node_normals

    def _set_part_label(self, part_name):
        if part_name == "upper_beam":
            return 1

        elif part_name == "lower_beam":
            return 2

        elif part_name == "crash_box":
            return 3

        elif part_name == "end_plate":
            return 4

        elif part_name == "tow_hook":
            return 5

        elif part_name == "bracket":
            return 6

        else:
            return 0

    def _recombine_dictionary_by_name(self, source_dict, part_name_mapping):
        """
        Reassemble all the parts according to their names

        :param source_dict:
        :param name_dict:
        :return:
        """

        category_rules = {
            "upper_beam": ["upper_beam", "up_beam"],
            "lower_beam": ["lower_beam", "low_beam"],
            "crash_box": ["crash_box", "cb"],
            "end_plate": ["end_plate", "bottom_plate"],
            "tow_hook": ["tow_hook", "towing_hook"],
            "bracket": ["bracket", "bkt"],
        }

        part_collector = {
            category: {"node_ids": [], "node_coords": [], "node_norms": [], "element_ids": [], "element_norms": [], "element_areas": [], "label": -1}
            for category in category_rules
        }

        for pid, data_dict in source_dict.items():
            p_name = part_name_mapping.get(pid, "").lower()

            for category, keywords in category_rules.items():
                if any(kw in p_name for kw in keywords):
                    part_collector[category]["node_ids"].append(data_dict["node_ids"])
                    part_collector[category]["node_coords"].append(data_dict["node_coords"])
                    part_collector[category]["node_norms"].append(data_dict["node_norms"])
                    part_collector[category]["element_ids"].append(data_dict["element_ids"])
                    part_collector[category]["element_norms"].append(data_dict["element_norms"])
                    part_collector[category]["element_areas"].append(data_dict["element_areas"])
                    part_collector[category]["label"] = self._set_part_label(part_name=category)
                    break

        for p_name, data_dict in part_collector.items():
            current_node_ids = data_dict["node_ids"]
            current_node_coords = data_dict["node_coords"]
            current_node_norms = data_dict["node_norms"]
            current_element_ids = data_dict["element_ids"]
            current_element_norms = data_dict["element_norms"]
            current_element_areas = data_dict["element_areas"]

            if len(current_node_ids) > 0:
                data_dict["node_ids"] = torch.cat(current_node_ids, dim=0)

            if len(current_node_coords) > 0:
                data_dict["node_coords"] = torch.cat(current_node_coords, dim=0)

            if len(current_node_norms) > 0:
                data_dict["node_norms"] = torch.cat(current_node_norms, dim=0)

            if len(current_element_ids) > 0:
                data_dict["element_ids"] = torch.cat(current_element_ids, dim=0)

            if len(current_element_norms) > 0:
                data_dict["element_norms"] = torch.cat(current_element_norms, dim=0)

            if len(current_element_areas) > 0:
                data_dict["element_areas"] = torch.cat(current_element_areas, dim=0)

        return part_collector

    def _tensor_dict_to_list_dict(self, source_dict):
        """
        translate tensor dict to list dict

        :param: tensor dict
        :return: list dict
        """
        if isinstance(source_dict, dict):
            return {key: self._tensor_dict_to_list_dict(value) for key, value in source_dict.items()}

        elif isinstance(source_dict, list):
            return [self._tensor_dict_to_list_dict(item) for item in source_dict]

        elif isinstance(source_dict, torch.Tensor):
            return source_dict.tolist()

        else:
            return source_dict

    def _unique_solid_surface(self, solid_surfaces):
        """
        :param solid_surfaces: solid surface elements
        :return: unique solid_surface elements
        """

        element_nids = solid_surfaces[:, 2:]
        element_nidx3 = element_nids[:, 2]
        element_nidx4 = element_nids[:, 3]

        mask = element_nidx3 == element_nidx4
        element_s3_nids = element_nids[mask]
        element_s4_nids = element_nids[~mask]

        element_s3 = solid_surfaces[mask]
        element_s4 = solid_surfaces[~mask]

        # s3
        sorted_element_s3_nids, _ = torch.sort(element_s3_nids[:, :3], dim=-1)

        unique_element_s3_nids, inverse_s3, counts_s3 = torch.unique(sorted_element_s3_nids, dim=0, return_inverse=True, return_counts=True)

        mask_s3_faces = counts_s3 == 1

        surface_s3_idx = mask_s3_faces[inverse_s3]

        solid_surface_s3_faces = element_s3[surface_s3_idx]

        # s4
        sorted_element_s4_nids, _ = torch.sort(element_s4_nids, dim=-1)

        unique_element_s4_nids, inverse_s4, counts_s4 = torch.unique(sorted_element_s4_nids, dim=0, return_inverse=True, return_counts=True)

        mask_s4_faces = counts_s4 == 1

        surface_s4_idx = mask_s4_faces[inverse_s4]

        solid_surface_s4_faces = element_s4[surface_s4_idx]

        unique_solid_surface_faces = torch.cat([solid_surface_s3_faces, solid_surface_s4_faces], dim=0)

        return unique_solid_surface_faces


tbox = TBox()
