

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
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';

import { useState } from "react";
import { shorten_string } from "../common/utils";

//const DEFAULT_COLORS = [grey[100], grey[200], grey[300], grey[400], grey[500]];
const DEFAULT_COLORS = [grey[100], grey[300]];

export function ContextNode(props: { context: Context, depth: number, opened: Set<string>, toggleOpen: (uuid: string) => void }) {
    //let [open, setOpen] = useState<boolean>(props.depth < 1);

    let c = props.context;
    let open = props.opened.has(c.uuid);
    //let depth = props.depth <= 4 ? props.depth : 4;
    //if (props.context.meta)
    let color = props.context.meta?.color;

    if (!color) {
        color = DEFAULT_COLORS[props.depth % 2];
    }

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
                <DataRenderer uuid={c.uuid + "/inputs"} data={c.inputs} opened={props.opened} toggleOpen={props.toggleOpen} />
            </p>}
            {c.result &&
                <p>
                    <strong>Result</strong><br />
                    <DataRenderer uuid={c.uuid + "/result"} data={c.result} opened={props.opened} toggleOpen={props.toggleOpen} />
                </p>
            }
            {c.error &&
                <p>
                    <strong>Error</strong><br />
                    <DataRenderer uuid={c.uuid + "/error"} data={c.error} hideType="error" opened={props.opened} toggleOpen={props.toggleOpen} />
                </p>
            }
            {c.children?.map((ctx) => <div style={{ paddingLeft: 15 }}>
                <ContextNode key={ctx.uuid} context={ctx} depth={props.depth + 1} opened={props.opened} toggleOpen={props.toggleOpen} /></div>)}
        </>
    }

    let short_result = c.result ? shorten_string(c.result) : null;

    return <Item style={{ backgroundColor: color }} variant="outlined">

        <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
        }}>
            <IconButton onClick={() => props.toggleOpen(c.uuid)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>{icon}
            {c.name} {short_result && <><ArrowRightAltIcon /> {short_result}</>} {c.kind ? " [" + c.kind + "]" : ""}
        </div>
        {open && body()}
    </Item >
}