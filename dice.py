#!/usr/bin/env python3


"""
Library for creating and rolling virtual dice.

One of the ways that dice can be constructed is by using a "dice formula" which
follows common nomenclature for defining how dice are structured in various TTRPGs.
What does a valid dice formula look like?

    d6                  -> 1d6+0
    1d6                 -> 1d6+0
    2d10                -> 2d10+0
    d12+1               -> 1d12+1
    1d4+1               -> 1d4+1
    20d6-5              -> 20d6-5
    8d10+1d4-1          -> (8d10+0) + (1d4-1)
    d20+5-1d4           -> (1d20+5) - (1d4+0)
    d20+2+4-1           -> (1d20+5)
    d8+1-2+3+d4         -> (1d8+2) + (1d4+0)
    2d10-1+7-2d4+1-1+2  -> (2d10+6) - (2d4+2)

(NOTE: whitespace is allowed anywhere except within a number
 i.e. no "1 2 d 1 0 + 2", must be at least "12 d 10 + 2" or similar)



Dice Formula Grammar
====================

dice    : die ((PLUS|MINUS) die)*
die     : integer? DELIM integer ((PLUS|MINUS) integer)*
integer : DIGIT+

DIGIT   : [0-9]
DELIM   : "d"
PLUS    : "+"
MINUS   : "-"
"""


__all__ = [
        "Die",
        "DiceBag",
        "roll",
        "roll_to_str",
        ]


from dataclasses import dataclass, field
from enum import StrEnum, auto
import random


########
# Dice #
########

@dataclass(frozen=True, slots=True)
class Die:
    sides: int
    num_dice: int = 1
    modifier: int = 0

    def __str__(self) -> str:
        if self.modifier == 0:
            return f"{self.num_dice}d{self.sides}"
        return f"{self.num_dice}d{self.sides}{self.modifier:+}"

    def roll(self) -> int:
        return sum(random.randint(1, self.sides) for _ in range(self.num_dice)) + self.modifier

    def roll_to_str(self) -> str:
        return f"Rolled {self}    = {self.roll()}"


@dataclass(frozen=True, slots=True)
class DiceBagItem:
    die: Die
    subtracted: bool = False

    def roll(self) -> int:
        multiplier = -1 if self.subtracted else 1
        return multiplier * self.die.roll()


@dataclass(frozen=True, slots=True)
class DiceBag:
    _bag: list[DiceBagItem] = field(default_factory=list)

    def __getitem__(self, key: int):
        return self._bag[key].die

    def __len__(self):
        return len(self._bag)

    def __str__(self) -> str:
        if not self._bag:
            return f"<empty {type(self).__name__}>"

        to_return = str(self._bag[0].die)
        for item in self._bag[1:]:
            to_return += f" {'-' if item.subtracted else '+'} {item.die}"

        return to_return

    @staticmethod
    def from_str(formula: str) -> 'DiceBag':
        """Construct a DiceBag from a dice formula.

        Generally, a dice formula is 1 or more dice
        (in the nomenclature [num]d<sides>[ +- <modifier>])
        that are added and subtracted from each other.

        Examples of dice formulas:
            d6          -> 1d6+0
            1d6         -> 1d6+0
            2d4+2       -> 2d4+2
            d10-3       -> 1d10-3
            d20+5-d4    -> (1d20+5) - (1d4)
            2d20+5+d4   -> (2d20+5) + (1d4)
            etc.

        Check the description of this module (e.g. help(__import__('dice')) )
        for a full breakdown of the grammar and more examples.
        """
        return Parser(formula).dice()

    def add_die(self, die: Die, *, subtracted: bool = False) -> None:
        self._bag.append(DiceBagItem(die, subtracted))

    def roll(self) -> int:
        return sum(die.roll() for die in self._bag)

    def roll_to_str(self) -> str:
        return f"Rolled {self}    = {self.roll()}"


######################
# Lexing and Parsing #
######################

class TokenType(StrEnum):
    INTEGER = auto()
    DELIM = auto()
    PLUS = auto()
    MINUS = auto()
    EOF = auto()

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


@dataclass(frozen=True, slots=True)
class Token:
    type: TokenType
    value: str | int | None


class Lexer:
    def __init__(self, text: str) -> None:
        if not text:
            raise ValueError(f"Invalid input text of: {text!r}")
        self.text = text
        self._pos = 0
        self.current_char = self.text[self._pos]

    @property
    def pos(self) -> int:
        return self._pos

    @pos.setter
    def pos(self, value: int) -> None:
        self._pos = value
        if value >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[value]

    def advance(self) -> None:
        self.pos += 1

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self) -> int:
        """
        dice    : die ((PLUS|MINUS) die)*
        die     : integer? DELIM integer ((PLUS|MINUS) integer)*
        integer : DIGIT+

        DIGIT   : [0-9]
        DELIM   : "d"
        PLUS    : "+"
        MINUS   : "-"
        """
        assert self.current_char is not None and self.current_char.isdecimal()
        result = ''
        while self.current_char is not None and self.current_char.isdecimal():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            self.skip_whitespace()

            if self.current_char.isdecimal():
                return Token(TokenType.INTEGER, self.integer())
            elif self.current_char == 'd':
                self.advance()
                return Token(TokenType.DELIM, 'd')
            elif self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')
            elif self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')

            raise ValueError(f"Invalid character {self.current_char!r} at index {self.pos}")

        return Token(TokenType.EOF, None)

    def peek_next_token(self, *, ahead: int = 1) -> Token:
        # This is a hack to emulate an LL(n) parser with real lookahead.
        # It is not efficient and it does not need to be. Quiet, you!
        assert ahead > 0, f"peek_next_token() must look ahead at least 1 token; got {ahead}"
        pos = self.pos
        for _ in range(ahead):
            token = self.get_next_token()
        self.pos = pos
        return token    # type: ignore


class Parser:
    def __init__(self, text: str) -> None:
        self.lexer = Lexer(text)
        self.current_token = self.lexer.get_next_token()

    def eat(self, expected_token_type: TokenType) -> None:
        if expected_token_type == self.current_token.type:
            self.current_token = self.lexer.get_next_token()
            return
        raise ValueError(f"Expected token with type {expected_token_type} but got {self.current_token.type}")

    def peek_next_token(self, *args, **kwargs) -> Token:
        return self.lexer.peek_next_token(*args, **kwargs)

    def die(self) -> Die:
        """
        die     : integer? DELIM integer ((PLUS|MINUS) integer)*
        integer : DIGIT+

        DIGIT   : [0-9]
        DELIM   : "d"
        PLUS    : "+"
        MINUS   : "-"
        """
        num_dice = 1
        modifier = 0

        if self.current_token.type == TokenType.INTEGER:
            token = self.current_token
            self.eat(TokenType.INTEGER)
            assert type(token.value) is int
            num_dice = token.value

        self.eat(TokenType.DELIM)
        token = self.current_token
        self.eat(TokenType.INTEGER)
        assert type(token.value) is int
        sides = token.value

        # If there is an operator followed by an integer next, this could
        # either be the modifier for the current die OR the start of a new die.
        # We put this in a while-loop because the parser will combine repeated
        # modifiers into a single one.
        #
        # E.g. modifier (^ denotes position of `current_token` within the text):
        #
        #   2d6+5    or    2d6+5+1d4    or    2d6+5+d4
        #      ^              ^                  ^
        #   (operator -> integer -> operator or EOF = modifier)
        #
        # E.g. no modifier (^ denotes position of `current_token` within the text):
        #
        #   2d6+5d4    or    2d6+d4
        #      ^                ^
        #   (operator -> integer -> delimiter = no modifier)
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            # if "the thing after this PLUS/MINUS is a not a modifier"
            if not (self.peek_next_token().type == TokenType.INTEGER
                    and self.peek_next_token(ahead=2).type != TokenType.DELIM):
                break

            if self.current_token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                token = self.current_token
                self.eat(TokenType.INTEGER)
                assert type(token.value) is int
                modifier += token.value
            else:
                self.eat(TokenType.MINUS)
                token = self.current_token
                self.eat(TokenType.INTEGER)
                assert type(token.value) is int
                modifier -= token.value

        return Die(sides, num_dice, modifier)

    def dice(self) -> DiceBag:
        """
        dice    : die ((PLUS|MINUS) die)*
        die     : integer? DELIM integer ((PLUS|MINUS) integer)?
        integer : DIGIT+

        DIGIT   : [0-9]
        DELIM   : "d"
        PLUS    : "+"
        MINUS   : "-"
        """
        to_return = DiceBag()
        to_return.add_die(self.die())

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                to_return.add_die(self.die())
            else:
                self.eat(TokenType.MINUS)
                to_return.add_die(self.die(), subtracted=True)

        return to_return


def roll(formula: str):
    return DiceBag.from_str(formula).roll()


def roll_to_str(formula: str):
    return DiceBag.from_str(formula).roll_to_str()


def main():
    print('Parses dice formulas (q or Q to quit)', end='\n\n')

    while True:
        text = input('dice> ')
        if text.strip() in ('q', 'Q'):
            break
        if not text or not text.strip():
            continue

        bag = DiceBag.from_str(text)
        print(f"\tRolled {bag}")
        print(f"\tGot {bag.roll()}")


if __name__ == '__main__':
    main()

