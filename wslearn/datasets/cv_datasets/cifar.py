from torchvision.datasets import CIFAR10, CIFAR100
from torchvision import transforms

from wslearn.datasets import Dataset
from wslearn.utils.data import TransformDataset , split_lb_ulb_balanced
from wslearn.utils.augmentation import RandAugment

import numpy as np

class Cifar(Dataset):

    def __init__(self, cifar, data_dir, num_lbl=4, num_ulbl=None, seed=None,
                 crop_size=32, crop_ratio=1, download=True,
                 return_ulbl_labels=False):

        self.cifar = cifar
        self.return_ulbl_labels = return_ulbl_labels

        self._define_transforms(crop_size, crop_ratio)

        self._get_dataset(num_lbl, num_ulbl, seed, data_dir, download)

    def _define_transforms(self, crop_size, crop_ratio):

        self.weak_transform = transforms.Compose([
            transforms.Resize(crop_size),
            transforms.RandomCrop(crop_size,
                                  padding=int(crop_size * (1 - crop_ratio)),
                                  padding_mode='reflect'),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.medium_transform = transforms.Compose([
            transforms.Resize(crop_size),
            transforms.RandomCrop(crop_size, padding=int(crop_size * (1 - crop_ratio)), padding_mode='reflect'),
            transforms.RandomHorizontalFlip(),
            RandAugment(1, 5),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.strong_transform = transforms.Compose([
            transforms.Resize(crop_size),
            transforms.RandomCrop(crop_size, padding=int(crop_size * (1 - crop_ratio)), padding_mode='reflect'),
            transforms.RandomHorizontalFlip(),
            RandAugment(3, 5),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.eval_transform = transforms.Compose([
            transforms.Resize(crop_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _get_dataset(self, num_lbl, num_ulbl, seed, data_dir, download):

        train = self.cifar(data_dir, train=True, download=download)
        X, y = train.data, train.targets
        X_lb, y_lb, X_ulb, y_ulb = split_lb_ulb_balanced(X, y, num_lbl=num_lbl,
                                                         num_ulbl=num_ulbl,
                                                         seed=seed)

        if self.return_ulbl_labels is False:
            y_ulb = None

        self.lbl_dataset = TransformDataset(X=X_lb, y=y_lb,
                                       weak_transform=self.weak_transform,
                                       medium_transform=self.strong_transform,
                                       strong_transform=self.strong_transform)

        self.ulbl_dataset = TransformDataset(X=X_ulb, y=y_ulb,
                                       weak_transform=self.weak_transform,
                                       medium_transform=self.medium_transform,
                                       strong_transform=self.strong_transform)

        test = self.cifar(data_dir, train=False, download=download)

        X, y = test.data, test.targets
        X, y = np.array(X), np.array(y)
        self.eval_dataset = TransformDataset(X=X, y=y,
                                        weak_transform=self.eval_transform)

class Cifar10(Cifar):
    def __init__(self, num_lbl=4, num_ulbl=None, seed=None,
                    crop_size=32, crop_ratio=1,
                    data_dir = "~/.wslearn/datasets/CIFAR10", download=True):
        super().__init__(CIFAR10, data_dir, num_lbl, num_ulbl, seed,
                         crop_size, crop_ratio, download)

class Cifar100(Cifar):
    def __init__(self, num_lbl=4, num_ulbl=None, seed=None,
                    crop_size=32, crop_ratio=1,
                    data_dir = "~/.wslearn/datasets/CIFAR100", download=True):
        super().__init__(CIFAR100, data_dir, num_lbl, num_ulbl, seed,
                         crop_size, crop_ratio, download)
