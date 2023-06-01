

import { Context } from "../model/Context";
import { Button, Divider, Fab, IconButton } from "@mui/material";

import { grey } from '@mui/material/colors';
import { Item } from "./Item";
import { DataRenderer } from "./DataRenderer";

import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ReplayIcon from '@mui/icons-material/Replay';
import ErrorIcon from '@mui/icons-material/Error';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

import { useState } from "react";

//const DEFAULT_COLORS = [grey[100], grey[200], grey[300], grey[400], grey[500]];
const DEFAULT_COLORS = [grey[100], grey[300]];

export function ContextNode(props: { context: Context, depth: number }) {
    let [open, setOpen] = useState<boolean>(props.depth < 1);

    let c = props.context;
    //let depth = props.depth <= 4 ? props.depth : 4;
    let color = DEFAULT_COLORS[props.depth % 2];

    let icon;

    if (c.state) {
        icon = <ErrorIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "repeat_on_failure") {
        icon = <ReplayIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "query") {
        icon = <QuestionMarkIcon style={{ paddingRight: 10 }} />
    } else {
        icon = <AccountTreeIcon style={{ paddingRight: 10 }} />
    }

    function body() {
        return <>
            {(c.inputs || c.result || c.error) && <Divider />}
            {c.inputs && <p>
                <strong>Inputs</strong><br />
                <DataRenderer data={c.inputs} />
            </p>}
            {c.result &&
                <p>
                    <strong>Result</strong><br />
                    <DataRenderer data={c.result} />
                </p>
            }
            {c.error &&
                <p>
                    <strong>Error</strong><br />
                    <DataRenderer data={c.error} hideType="error" />
                </p>
            }
            {c.children?.map((ctx) => <div style={{ paddingLeft: 15 }}><ContextNode key={ctx.uuid} context={ctx} depth={props.depth + 1} /></div>)}
        </>
    }

    return <Item style={{ backgroundColor: color }} variant="outlined">

        <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
        }}>
            <IconButton onClick={() => setOpen(!open)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>{icon}
            {c.name} {c.kind ? ": " + c.kind : ""}
        </div>
        {open && body()}
    </Item >
}