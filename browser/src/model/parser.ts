
export enum TokenType {
    Ident,
    Operator,
    Literal,
    LiteralNum,
}

export type TokenIdent = {
    type: TokenType.Ident,
    value: string[],
}

export type TokenOperator = {
    type: TokenType.Operator,
    value: string,
}

export type TokenLiteral = {
    type: TokenType.Literal,
    value: string | number,
}

export type Token = TokenIdent | TokenOperator | TokenLiteral;


class TokenStream {

    private str: string;
    private index: number;

    constructor(str: string) {
        this.str = str;
        this.index = 0;
    }

    public consumeChar(fn: (c: string) => boolean): string | null {
        const index = this.index;
        if (index >= this.str.length) {
            return null;
        }
        const c = this.str[index];
        if (fn(c)) {
            return c;
        } else {
            return null;
        }
    }

    public nextToken(): Token | null {
        while (this.consumeChar((c) => c === " " || c === "\t" || c === "\n")) { }
        return null;
    }

}