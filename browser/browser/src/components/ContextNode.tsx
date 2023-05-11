

import { Context } from "../model/Context";
import { Divider } from "@mui/material";

import { grey } from '@mui/material/colors';
import { Item } from "./Item";
import { DataRenderer } from "./DataRenderer";

import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ReplayIcon from '@mui/icons-material/Replay';
import ErrorIcon from '@mui/icons-material/Error';

//const DEFAULT_COLORS = [grey[100], grey[200], grey[300], grey[400], grey[500]];
const DEFAULT_COLORS = [grey[100], grey[300]];

export function ContextNode(props: { context: Context, depth: number }) {
    let c = props.context;
    let depth = props.depth <= 4 ? props.depth : 4;
    let color = DEFAULT_COLORS[depth % 2];

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

    return <Item style={{ backgroundColor: color }} variant="outlined">

        <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            paddingBottom: 10,
        }}>
            {icon}
            {c.name} {c.kind ? ": " + c.kind : ""}
        </div>
        <Divider />
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
    </Item >
}