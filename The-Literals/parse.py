from run_code import apply_binop, apply_comparison
from tokenise import Token, Tokeniser


class UnexpectedTokenError(RuntimeError):
    def __init__(self, expected_token, actual_token):
        self.expected_token = expected_token
        self.actual_token = actual_token

    def __str__(self):
        return f"Expected {self.expected_token} but found {self.actual_token}"


class Parser:
    def __init__(self, get_token):
        self.get_token = get_token
        self.current_lexeme = None
        self.next_lexeme = self.get_token()

    def peek_lexeme(self):
        return self.next_lexeme

    def advance(self):
        self.current_lexeme = self.next_lexeme
        if self.current_lexeme[0] != Token.EOF:
            self.next_lexeme = self.get_token()
        return self.current_lexeme

    def expect(self, expected_token):
        token, value = self.advance()
        if token != expected_token:
            raise UnexpectedTokenError(expected_token, token)
        return token, value

    def parse(self):
        print(self.parse_program())

    def parse_program(self):
        self.expect(Token.BOF)
        self.parse_stmt()
        self.expect(Token.EOF)

    def parse_stmts(self):
        stmts_end_tokens = [Token.LEAVE_FUNC, Token.EOF]
        done = False
        while not done:
            token, value = self.peek_lexeme()
            if token in stmts_end_tokens:
                done = True
            else:
                self.parse_stmt()

    def parse_stmt(self):
        self.parse_stmt_contents()
        self.expect(Token.DOT)

    def parse_stmt_contents(self):
        token, value = self.advance()
        if token == Token.SETVAR:
            self.parse_set_stmt()
        elif token == Token.IF_KEYWORD:
            self.parse_if_stmt()

    def parse_set_stmt(self):
        target = self.parse_identifier()
        token, value = self.advance()
        if token != Token.TO:
            raise UnexpectedTokenError(Token.TO, token)
        self.parse_operand()

    def parse_identifier(self):
        identifier_words = []
        token, value = self.peek_lexeme()
        while token == Token.IDENTIFIER_WORD:
            identifier_words.append(value)
            self.advance()
            token, value = self.peek_lexeme()
        return ' '.join(identifier_words)

    def parse_if_stmt(self):
        condition = self.parse_expr()
        self.expect(Token.THEN)
        stmt = self.parse_stmt_contents()
        if condition:
            stmt.run()

    def parse_expr(self):
        first_operand = self.parse_operand()
        operator_token, operator_value = self.peek_lexeme()
        if operator_token == Token.BINOP or operator_token == Token.COMPARISON:
            return self.parse_operation(
                first_operand, operator_token, operator_value
            )
        else:
            return first_operand



    def parse_operation(self, first_operand_value, operator_token, operator_value):
        self.advance()  # we already have these values!
        second_operand_token, second_operand_value = self.advance()
        if second_operand_token != Token.NUMBER:
            raise UnexpectedTokenError(Token.NUMBER, second_operand_token)
        if operator_token == Token.BINOP:
            result = Binop(
                operator_value, first_operand_value, second_operand_value
            )
        if operator_token == Token.COMPARISON:
            result = apply_comparison(
                operator_value, first_operand_value, second_operand_value
            )
        return result

    def parse_operand(self):
        token, value = self.peek_lexeme()
        if token == Token.NUMBER:
            operand_token, operand_value = self.expect(Token.NUMBER)
        elif token == Token.IDENTIFIER_WORD:
            self.parse_identifier()
        else:
            raise UnexpectedTokenError(
                Token.IDENTIFIER_WORD, token
            )  # TODO: could be either.

if __name__ == "__main__":

    def empty_program():
        yield (Token.BOF, "")
        yield (Token.EOF, "")

    def set_var_to_constant():
        yield (Token.BOF, "")
        yield (Token.SETVAR, "Set")
        yield (Token.IDENTIFIER_WORD, "x")
        yield (Token.TO, "to")
        yield (Token.NUMBER, "-39")
        yield (Token.DOT, ".")
        yield (Token.EOF, "")

    def expr():
        yield (Token.NUMBER, "-98")
        yield (Token.BINOP, "-")
        yield (Token.NUMBER, "100")
        yield (Token.EOF, "")

    def set_var_to_var():
        yield (Token.BOF, "")
        yield (Token.SETVAR, "Set")
        yield (Token.IDENTIFIER_WORD, "retirement")
        yield (Token.IDENTIFIER_WORD, "age")
        yield (Token.TO, "to")
        yield (Token.IDENTIFIER_WORD, "pension")
        yield (Token.IDENTIFIER_WORD, "age")
        yield (Token.DOT, ".")
        yield (Token.EOF, "")

    def if_stmt_compare_constants():
        yield (Token.BOF, "")
        yield (Token.IF_KEYWORD, "If")
        yield (Token.NUMBER, "6800")
        yield (Token.COMPARISON, "is")
        yield (Token.NUMBER, "6800")
        yield (Token.THEN, "then")
        yield (Token.SETVAR, "set")
        yield (Token.IDENTIFIER_WORD, "successor")
        yield (Token.TO, "to")
        yield (Token.NUMBER, "68000")
        yield (Token.DOT, ".")
        yield (Token.EOF, "")

    def if_stmt_compare_variable_and_constant():
        yield (Token.BOF, "")
        yield (Token.IF_KEYWORD, "If")
        yield (Token.IDENTIFIER_WORD, "processor")
        yield (Token.IDENTIFIER_WORD, "type")
        yield (Token.COMPARISON, "is")
        yield (Token.NUMBER, "6800")
        yield (Token.THEN, "then")
        yield (Token.SETVAR, "set")
        yield (Token.IDENTIFIER_WORD, "processor")
        yield (Token.IDENTIFIER_WORD, "type")
        yield (Token.TO, "to")
        yield (Token.NUMBER, "68000")
        yield (Token.DOT, ".")
        yield (Token.EOF, "")

    def if_stmt_compare_variable_and_variable():
        yield (Token.BOF, "")
        yield (Token.IF_KEYWORD, "If")
        yield (Token.IDENTIFIER_WORD, "processor")
        yield (Token.IDENTIFIER_WORD, "type")
        yield (Token.COMPARISON, "is")
        yield (Token.IDENTIFIER_WORD, "eight")
        yield (Token.IDENTIFIER_WORD, "bit")
        yield (Token.THEN, "then")
        yield (Token.SETVAR, "set")
        yield (Token.IDENTIFIER_WORD, "processor")
        yield (Token.IDENTIFIER_WORD, "architecture")
        yield (Token.TO, "to")
        yield (Token.NUMBER, "6502")
        yield (Token.DOT, ".")
        yield (Token.EOF, "")

    parser = Parser(set_var_to_constant().__next__)
    parser.parse()

    parser = Parser(set_var_to_var().__next__)
    parser.parse()

    parser = Parser(if_stmt_compare_constants().__next__)
    parser.parse()

    parser = Parser(if_stmt_compare_variable_and_constant().__next__)
    parser.parse()

    parser = Parser(if_stmt_compare_variable_and_variable().__next__)
    parser.parse()
