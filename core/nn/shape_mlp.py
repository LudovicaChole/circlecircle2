import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.nn.nbox import FeaturesToTensorExtractor
from core.nn.nbox import PartNodeFeaturesDataset
from core.nn.nbox import FeatureEmbedding
from core.nn.nbox import PointsShapeMLP
from core.nn.nbox import DataLoader
from core.nn.nbox import optim
from core.nn.nbox import Trainer
from core.nn.nbox import nn
from core.nn.nbox import ModelSaver


class ShapeMLPServicer:
    def __init__(self, file_path, input_features, output_features, batch_size, epochs):
        self.name = "ShapeMLPServicer"
        self.file_path = file_path
        self.input_features = input_features
        self.output_features = output_features

        self.part_node_features = FeaturesToTensorExtractor().part_node_features(file_path=file_path,
                                                                                 num_points=2048)

        self.part_node_features_dataset = PartNodeFeaturesDataset(features_list=self.part_node_features)
        print(f"length dataset is {len(self.part_node_features_dataset)}")

        self.feature_embedding = FeatureEmbedding(input_dim=6, output_dim=input_features)

        self.points_shape_mlp = PointsShapeMLP(embedding=self.feature_embedding,
                                               input_features=input_features,
                                               output_features=output_features,
                                               hidden_layers=[input_features * 3, input_features * 2, int(input_features * 0.5)])

        self.part_node_dataloader = DataLoader(dataset=self.part_node_features_dataset,
                                               batch_size=batch_size,
                                               shuffle=True)

        self.part_node_optimizer = optim.Adam(self.points_shape_mlp.parameters(), lr=0.002)

        self.part_node_trainer = Trainer(model=self.points_shape_mlp,
                                         dataloader=self.part_node_dataloader,
                                         optimizer=self.part_node_optimizer,
                                         loss_fn=nn.CrossEntropyLoss(),
                                         epochs=epochs)

        self.model_saver = ModelSaver()

    def train(self):
        self.part_node_trainer.train()

        self.model_saver.save(model=self.points_shape_mlp,
                              file_path=self.file_path)


if __name__ == '__main__':

    file_path = str(Path(__file__).resolve().parents[2] / 'test/ShapeMLP/test_model.json')
    folder_path = str(Path(__file__).resolve().parents[2] / 'test/ShapeMLP')

    shape_mlp = ShapeMLPServicer(file_path=file_path,
                                 input_features=128,
                                 output_features=7,
                                 batch_size=16,
                                 epochs=100)

    shape_mlp.train()

