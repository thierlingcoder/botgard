import datetime
import csv
from pathlib import Path
from copy import deepcopy
from typing import Type, List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import models

from plant.models import Category, Plant
from seeds.models import Seeds


class Command(BaseCommand):
    help = 'Add demo data to the database'

    def handle(self, *args, **options):
        add_demo_data()



def add_demo_data():
    demo_path = Path(settings.BASE_DIR) / "demo-data"

    category_list = _read_csv(demo_path / "category.csv")
    plant_list = _read_csv(demo_path / "plant.csv")
    seeds_list = _read_csv(demo_path / "seeds.csv")

    category_id_map = _add_to_database(Category, category_list)

    for data in plant_list:
        data["category"] = category_id_map[int(data["category"])]

    plant_id_map = _add_to_database(Plant, plant_list)

    for data in seeds_list:
        data["plant"] = plant_id_map[int(data["plant"])]

    _add_to_database(Seeds, seeds_list)


def _read_csv(filename: Path):
    with filename.open() as fp:
        data_list = list(csv.DictReader(fp))

    for entry in data_list:
        entry["id"] = int(entry["id"])

    return data_list


def _add_to_database(Model: Type[models.Model], data_list: List[dict]) -> dict:
    id_map = {}
    for data in data_list:
        data = deepcopy(data)

        table_id = data.pop("id")

        for key, value in data.items():
            if key.endswith("_date"):
                if not value.strip():
                    data[key] = None

        instance = Model.objects.create(**data)

        id_map[table_id] = instance

    return id_map




