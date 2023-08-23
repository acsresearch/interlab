import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';


const TOKEN_REGEXP = /([\w.]+)|(\d+)|([=<>]+)|\"(?:\\\"|[^\"])*\"|./g
//const TOKEN_REGEXP = /[\w.]+|\d+|[=<>]+|\"(?:\\\"|[^\"]*\")/

test('renders learn react link', () => {
    //console.log("a.bbb= \"xxx\" < 1".match(TOKEN_REGEXP))
    const s = "a.bbb= \"xxx\" < $ 1 ";

    //console.log(TOKEN_REGEXP.exec(s));

    for (const result of s.matchAll(TOKEN_REGEXP)) {
        console.log(">>>", result)
    }
});
