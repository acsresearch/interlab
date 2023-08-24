
export enum TokenType {
    Ident = "ident",
    Operator = "op",
    LiteralStr = "literal_s",
    LiteralNum = "literal_n",
}

export type Token = {
    type: TokenType,
    index: number,
    value: string | number,
}

//export type Token = TokenIdent | TokenOperator | TokenLiteral;

const TOKEN_REGEXP = /(?<ident>[A-Za-z][\w.]*)|(?<int>\d+)|(?<op>[=<>]+)|\"(?<str>(?:\\\"|[^\"]))*\"|(?<space>\s+)|./g

export function parse_tokens(input: string): Token[] {
    const tokens: Token[] = [];
    for (const match of input.matchAll(TOKEN_REGEXP)) {
        if (match.groups.space) {
            continue
        }
        let value = match[0]
        let token_type: TokenType | undefined;
        if (match.groups.ident) {
            token_type = TokenType.Ident;
        } else if (match.groups.op) {
            token_type = TokenType.Operator;
        } else if (match.groups.int) {
            token_type = TokenType.LiteralNum;
            value = +value;
        } else if (match.groups.str) {
            token_type = TokenType.LiteralStr;
        } else {
            throw new Error("Invalid token");
        }
        tokens.push({ type: token_type, value, index: match.index })
        // console.count(`xxx <${first}>`)
        // if (first.match(/\s/)) {
        //     continue
        // }
        // if (first.match(/[A-Za-z]/)) {
        //     tokens.push({ type: TokenType.Ident, value, index })
        //     continue
        // }
        // if (first.match(/[A-Za-z]/)) {
        //     tokens.push({ type: TokenType.Ident, value, index })
        //     continue
        // }

    }
    return tokens;
}