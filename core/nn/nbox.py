import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from torch.utils.data import Dataset
import json
import os
from utilities.logger import logger


class FeaturesToTensorExtractor:
    """
    format:
    list[part_features_dict1, part_features_dict2, ...]

    usage:
    dataset data must be saved at cpu !!!
    self.device = "cpu"

    features_to_tensor_extractor = FeaturesToTensorExtractor()
    part_node_features = features_to_tensor_extractor.part_node_features(file_path=file_path, num_points=1024)
    part_node_features_dataset = PartNodeFeaturesDataset(features_list=part_node_features)

    """
    def __init__(self):
        self.logger = logger
        self.device = "cpu"

    # only extract node features from .json, [x, y, z, n1, n2, n3]
    def part_node_features(self, file_path, num_points):
        if os.path.isfile(file_path):

            current_part_features = self.single_file_to_tensor(file_path=file_path, num_points=num_points)

            return current_part_features

        elif os.path.isdir(file_path):
            all_part_features = []

            with os.scandir(file_path) as entries:
                for entry in entries:
                    if entry.is_file():
                        current_part_features = self.single_file_to_tensor(file_path=entry.path, num_points=num_points)
                        all_part_features.extend(current_part_features)

            return all_part_features

        else:
            self.logger.warning(f"File {file_path} not found\n")

            return None

    def single_file_to_tensor(self, file_path, num_points):
        current_part_features = []

        with open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
            current_dict = json.load(f)

        # Combine the coordinates and normal of each part, along dim=1, [x, y, z, n1, n2, n3]
        for part_name, value in current_dict.items():
            part_coords = value["node_coords"]
            part_norms = value["node_norms"]
            part_label = value["label"]

            if len(part_coords) > 0:
                part_coords_tensor = torch.tensor(part_coords, dtype=torch.float32, device=self.device)
                part_norms_tensor = torch.tensor(part_norms, dtype=torch.float32, device=self.device)
                part_labels_tensor = torch.tensor(part_label, dtype=torch.long, device=self.device)

                part_node_features_tensor = torch.cat((part_coords_tensor, part_norms_tensor), dim=1)

                part_node_features_tensor = self.sampled_for_node_features(features_tensor=part_node_features_tensor,
                                                                           num_points=num_points, )

                current_sample = {
                    "part_name": part_name,
                    "features": part_node_features_tensor,
                    "label": part_labels_tensor
                }

                current_part_features.append(current_sample)

        return current_part_features

    def sampled_for_node_features(self, features_tensor, num_points):
        """
        :param features_tensor: features_tensor
        :param num_points: user define number of dim
        :return:
        """

        shape_0 = features_tensor.shape[0]

        if shape_0 == 0:
            raise ValueError("Empty point cloud")

        # If the input data is greater than num_points, a random sampling method is used
        elif shape_0 > num_points:
            idx = torch.randperm(n=shape_0, device=features_tensor.device)[: num_points]

            sampled = features_tensor[idx]

        # If the input data is less than num_points, a repeated sampling method is used
        elif shape_0 < num_points:
            repeat_num = num_points - shape_0

            idx = torch.randint(low=0,
                                high=shape_0,
                                size=(repeat_num,),
                                device=features_tensor.device)

            extra_features = features_tensor[idx]

            coords = extra_features[:, :3]
            normals = extra_features[:, 3:]

            noise = torch.randn_like(coords)

            coords = coords + noise * 0.01

            # extra_features = extra_features + noise * 0.01
            extra_features = torch.cat((coords, normals), dim=1)

            sampled = torch.cat((features_tensor, extra_features), dim=0)

        else:
            sampled = features_tensor

        return sampled


class PartNodeFeaturesDataset(Dataset):
    """
    get node coords and node norms from .json

    usage:

    """
    def __init__(self, features_list):
        self.logger = logger
        self.features_list = features_list

    def __len__(self):
        return len(self.features_list)

    def __getitem__(self, idx):
        current_feature = self.features_list[idx]

        x = current_feature["features"]
        y = current_feature["label"]

        return x, y


class FeatureEmbedding(nn.Module):
    """
    Transform node features into a higher-dimensional space
    node features [x, y, z, n1, n2, n3]
    higher-dimensional features [x1, x2, x3, x4, x5, ,x6, ...]
    """
    def __init__(self,
                 input_dim: int,
                 output_dim: int):
        super().__init__()

        mid_dim = int(output_dim / 2)

        self.encoder = nn.Sequential(nn.Linear(input_dim, mid_dim),
                                     nn.ReLU(),
                                     nn.Linear(mid_dim, output_dim))

    def forward(self, x):
        x = self.encoder(x)

        return x


class PointsShapeMLP(nn.Module):
    """
    example:
    ------------------------------------------------------------------------
    model = MLP(
        input_features=9,
        output_features=2,
        hidden_layers=[64, 16]
    )
    ------------------------------------------------------------------------

    input_features = 9
    hidden_layers = [64, 16]
    output_features = 2

    dims = [input_features] + hidden_layers + [output_features] ---->
    dims = [9] + [64, 16] + [2]
    dims = [9, 64, 16, 2]

    nn.Linear(input_features, output_features)

    ...

    """
    def __init__(self,
                 embedding,
                 input_features: int,
                 output_features: int,
                 hidden_layers: list[int],
                 activation=nn.ReLU,
                 dropout: float = 0.0,    # randomly deactivate a portion of neurons; value is between 0.0 and 0.2
                 ):
        super().__init__()

        self.embedding = embedding
        self.input_features = input_features
        self.output_features = output_features
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.dropout = dropout
        self.user_net = None

        self.initialize()

    def initialize(self):

        collector = []    # empty sequential list

        all_dims = [self.input_features] + self.hidden_layers + [self.output_features]

        for i in range(len(all_dims)-1):
            current_input_features = all_dims[i]

            current_output_features = all_dims[i+1]

            current_linear = nn.Linear(current_input_features, current_output_features)

            collector.append(current_linear)

            # Add ReLU function
            if i != len(all_dims) - 2:
                collector.append(self.activation())

                # Randomly drop out a portion of neurons.
                if self.dropout > 0:
                    current_dropout = nn.Dropout(p=self.dropout)
                    collector.append(current_dropout)

        self.user_net = nn.Sequential(*collector)

    def forward(self, x):
        high_dim_features = self.embedding(x)

        max_pool_features = torch.max(high_dim_features, dim=1)[0]

        return self.user_net(max_pool_features)


class Trainer:
    """
    example:
    trainer = Trainer(model=model,
                  dataloader=dataloader,
                  optimizer=optimizer,
                  loss_fn=nn.CrossEntropyLoss(),
                  epochs=50)

    trainer.train()

    nn.CrossEntropyLoss(): normally used to categorize items, like 1 is Cat, 2 is Dog
    nn.MSELoss(): normally used to predict continuous numerical values

    If it is used for a regression task, disable dropout, set dropout to 0.0
    If it is used for a classification task, set dropout to 0.1 - 0.2, normally
    """
    def __init__(self, model, dataloader, optimizer, loss_fn, epochs):
        self.model = model
        self.dataloader = dataloader
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.epochs = epochs
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logger
        self.logger.debug(f"device is {self.device}\n")

    def train(self):
        self.model.to(self.device)

        for epoch in range(self.epochs):
            self.model.train()

            running_loss = 0.0

            for batch_x, batch_y in self.dataloader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)

                self.optimizer.zero_grad()

                output = self.model(batch_x)

                loss = self.loss_fn(output, batch_y)

                loss.backward()

                self.optimizer.step()

                running_loss += loss.item()

            average_loss = running_loss / len(self.dataloader)

            self.logger.debug(f"Epoch: {epoch+1}, Loss: {average_loss}")


class ModelSaver:
    def __init__(self):
        self.logger = logger

    def save(self, model, file_path):
        if os.path.isdir(file_path):
            saved_path = os.path.join(file_path, "model.pth")

            torch.save(model.state_dict(), saved_path)

            self.logger.info(f"Model saved to {saved_path}")

        else:
            saved_path = os.path.join(os.path.dirname(file_path), "model.pth")

            torch.save(model.state_dict(), saved_path)

            self.logger.info(f"Model saved to {saved_path}")


class DatasetTester:
    """
    to test dataset work successfully

    usage:

    dataset_tester = TestDataset(data_type="mlp")

    dataset_tester.test(dataset)

    dataset_tester = DatasetTester()
    dataset_tester.test(data_type="part_node",
                        dataset=part_node_features_dataset)
    """
    def __init__(self):
        self.logger = logger

    def test(self, data_type, dataset):
        self.logger.debug(f"Testing dataset:")

        if data_type == "part_node":
            length = len(dataset)
            self.logger.debug(f"include data batch: {length}\n")

            for i in range(length):
                current_data = dataset[i]

                x = current_data[0]
                y = current_data[1]

                self.logger.debug(f"current_part_label: {y}")
                self.logger.debug(f"x shape is {x.shape}, y shape is {y.shape}\n")
        elif data_type == "part_element":
            pass

        else:
            pass

