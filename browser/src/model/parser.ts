
export enum TokenType {
    Ident,
    Operator,
    Literal,
    LiteralNum,
}

export type Token = {
    type: TokenType,
    index: number,
    value: string,
}

//export type Token = TokenIdent | TokenOperator | TokenLiteral;

const TOKEN_REGEXP = /([\w.]+)|(\d+)|([=<>]+)|\"(?:\\\"|[^\"])*\"|./g

function parse_tokens(input: string): Token[] {
    for (const match of input.matchAll(TOKEN_REGEXP)) {
        const value = match[0]
        const index = match.index;
    }
}