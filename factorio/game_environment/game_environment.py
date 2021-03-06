from pathlib import Path
from typing import Union

from factorio.crafting_tree_builder.internal_types.material import Material
from factorio.crafting_tree_builder.internal_types.recipes_collection import RecipesCollection
from factorio.game_environment.object_stats.a_stats import AStats
from factorio.game_environment.object_stats.assembling_machine_stats import AssemblingMachineStats
from factorio.game_environment.object_stats.crafting_category import CraftingCategory
from factorio.game_environment.object_stats.fluid_stats import FluidStats
from factorio.game_environment.object_stats.inserter_stats import InserterStats
from factorio.game_environment.object_stats.item_stats import ItemStats
from factorio.game_environment.object_stats.material_type import MaterialType
from factorio.game_environment.object_stats.mining_drill_stats import MiningDrillStats
from factorio.game_environment.object_stats.recipe_stats import RecipeStats
from factorio.game_environment.object_stats.transport_belt_stats import TransportBeltStats
from factorio.game_environment.stats_reading import read_stats_file


class GameEnvironment:

    def __init__(self,
                 recipe_stats: dict[str, RecipeStats],
                 item_stats: dict[str, ItemStats],
                 fluid_stats: dict[str, FluidStats],
                 assemblers_stats: dict[str, AssemblingMachineStats],
                 *other_stats_dicts: dict[str, AStats]):

        self.assemblers_stats = assemblers_stats
        self.item_stats = item_stats
        self.fluid_stats = fluid_stats

        self._other_stats_map = {}
        for stats in other_stats_dicts:
            self._other_stats_map = dict(self._other_stats_map, **stats)

        self._category_map: dict[CraftingCategory, list[str]] = {}
        self._init_categories()

        self.recipe_collection: RecipesCollection = self.create_recipes_collection(recipe_stats.values())

    @staticmethod
    def from_folder(load_folder: Path):
        recipe_stats = read_stats_file(load_folder / "recipe.json", RecipeStats)
        fluid_stats = read_stats_file(load_folder / "fluid.json", FluidStats)
        item_stats = read_stats_file(load_folder / "item.json", ItemStats)
        inserter_stats = read_stats_file(load_folder / "inserter.json", InserterStats)
        transport_belt_stats = read_stats_file(load_folder / "transport-belt.json", TransportBeltStats)
        assembling_stats = read_stats_file(load_folder / "assembling-machine.json", AssemblingMachineStats)
        furnace_stats = read_stats_file(load_folder / "furnace.json", AssemblingMachineStats)
        mining_stats = read_stats_file(load_folder / "mining-drill.json", MiningDrillStats)
        return GameEnvironment(recipe_stats,
                               item_stats,
                               fluid_stats,
                               dict(**assembling_stats, **furnace_stats),
                               inserter_stats,
                               transport_belt_stats,
                               mining_stats,)

    def get_placeable_stats(self, item_name: str) -> AStats:
        if isinstance(item_name, str):
            if item_name in self.assemblers_stats:
                return self.assemblers_stats[item_name]
            elif item_name in self._other_stats_map:
                return self._other_stats_map[item_name]

        raise ValueError(f'provide existing name string, not "{repr(item_name)}"')

    def get_material_stats(self, material):
        name = Material.name_from(material)
        if name in self.item_stats:
            return self.item_stats[name]
        elif name in self.fluid_stats:
            return self.fluid_stats[name]
        else:
            raise ValueError(f'provide existing name string, not "{repr(name)}"')

    def category_to_assemblers(self, category: CraftingCategory):
        return [self.get_placeable_stats(name).to_game_object() for name in self._category_map[category]]

    def get_material_type(self, material: Union[str, Material]):
        name = Material.name_from(material)
        if name in self.item_stats:
            return MaterialType.ITEM
        if name in self.fluid_stats:
            return MaterialType.FLUID
        raise ValueError("material not found")

    def _init_categories(self):
        assembler: AssemblingMachineStats
        for assembler in self.assemblers_stats.values():
            for _category in assembler.crafting_categories.keys():
                if _category not in self._category_map:
                    self._category_map[_category] = []
                self._category_map[_category].append(assembler.name)

    @staticmethod
    def create_recipes_collection(recipe_stats):
        recipes_collection = RecipesCollection()
        for _stats in recipe_stats:
            _recipe = _stats.to_game_object()
            if _recipe is not None:
                recipes_collection.add_unique_recipe(_recipe)

        for _unresolved_material in recipes_collection.get_unresolved_names():
            recipes_collection.add_unique_basic_material(_unresolved_material)

        return recipes_collection

    @staticmethod
    def load_default():
        return GameEnvironment.from_folder(Path('/home/anton/.factorio/script-output/recipe-lister/'))
