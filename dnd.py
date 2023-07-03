#!/usr/bin/env python3

import dataclasses
from enum import StrEnum, auto
from typing import Any


class Ability(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return name.title()

    STRENGTH = auto()
    DEXTERITY = auto()
    CONSTITUTION = auto()
    INTELLIGENCE = auto()
    WISDOM = auto()
    CHARISMA = auto()


@dataclasses.dataclass(frozen=True, slots=True)
class Proficiency:
    name: str


# class Proficiency(StrEnum):
#     @staticmethod
#     def _generate_next_value_(name: str, start, count, last_values):
#         return name.replace('_', ' ').title()
#
#
# class SkillProficiency(Proficiency):
#     pass
#
#
# class StrengthSkill(SkillProficiency):
#     SAVING_THROWS = auto()
#     ATHLETICS = auto()
#
#
# class DexteritySkill(SkillProficiency):
#     SAVING_THROWS = auto()
#     ACROBATICS = auto()
#     SLEIGHT_OF_HAND = auto()
#     STEALTH = auto()
#
#
# class ConstitutionSkill(SkillProficiency):
#     SAVING_THROWS = auto()
#
#
# class IntelligenceSkill(SkillProficiency):
#     SAVING_THROWS = auto()
#     ARCANA = auto()
#     HISTORY = auto()
#     INVESTIGATION = auto()
#     NATURE = auto()
#     RELIGION = auto()
#
#
# class WisdomSkill(SkillProficiency):
#     SAVING_THROWS = auto()
#     ANIMAL_HANDLING = auto()
#     INSIGHT = auto()
#     MEDICINE = auto()
#     PERCEPTION = auto()
#     SURVIVAL = auto()
#
#
# class CharismaSkill(SkillProficiency):
#     SAVING_THROWS = auto()
#     DECEPTION = auto()
#     INTIMIDATION = auto()
#     PERFORMANCE = auto()
#     PERSUASION = auto()


@dataclasses.dataclass
class Character:
    """
    Parts of a D&D 5e Character Sheet (alternative sheet style):

    PAGE 1 - Character Information
    ===================================================================
    - Header
        - Character Name
        - Class & Level
        - Background
        - Player Name
        - Race
        - Alignment
        - Experience Points
    - Ability Scores
        - Proficiency Bonus
        - Inspiration
        - Strength Score (and Modifier)
        - Dexterity Score (and Modifier)
        - Constitution Score (and Modifier)
        - Intelligence Score (and Modifier)
        - Wisdom Score (and Modifier)
        - Charisma Score (and Modifier)
        - Passive Wisdom (Perception)
        - Saving Throws
        - Skills
    - Combat Stats
        - Armor Class (10 + dex mod unarmored OR armor value + dex mod OR armor value for heavy armor)
        - Initiative (dex mod)
        - Speed (determined by race at lvl 1; some features increase this)
        - Hit Point Maximum
        - Current Hit Points
        - Temporary Hit Points
        - Total Hit Dice
        - Current Hit Dice
        - Death Saves (Successes and Failures)
    - Character Information
        - Personality Traits
        - Ideals
        - Bonds
        - Flaws
    - Attacks And Spellcasting
        - (3 spots for common attacks used)
        - Text area for writing down anything else
    - Features and Traits
        - (Big box for racial features and class features)
    - Other Proficiencies and Languages
        - Language Proficiencies
        - Tool Proficiencies
        - Weapon Proficiencies
        - Armor Proficiencies
    - Equipment and Character Notes
        - (Big box for whatever)

    PAGE 2 - Appearance, Flavour Text, and Extra space for Page 1 stuff
    ===================================================================
    - Age
    - Height
    - Weight
    - Eyes
    - Skin
    - Hair
    - Allies and Organizations
        - Picture of a symbol of an organization
        - Name of the symbol
    - Character Backstory
    - Additional Features and Traits
    - Treasure

    PAGE 3 - Spells
    ===================================================================
    - Spellcasting Class
    - Spellcasting Ability
    - Spell Save DC (8 + Proficiency Bonus + Spellcasting Ability Modifier)
    - Spell Attack Bonus (Proficiency Bonus + Spellcasting Ability Modifier)
    - Spells Known and Prepared
    - Spell Slots
    """
    pass

