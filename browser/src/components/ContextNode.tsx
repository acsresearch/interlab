

import { Context, duration, getAllChildren } from "../model/Context";
import { CircularProgress, Divider, IconButton, ListItemIcon, ListItemText, Menu, MenuItem } from "@mui/material";

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
import VisibilityIcon from '@mui/icons-material/Visibility';
import ForwardIcon from '@mui/icons-material/Forward';
import MenuIcon from '@mui/icons-material/Menu';
import CircleIcon from '@mui/icons-material/Circle';


import { humanReadableDuration, short_repr } from "../common/utils";
import PopupState, { bindMenu, bindTrigger } from "material-ui-popup-state";
import { Opener, OpenerMode } from "./DataBrowser";
import { TagChip } from "./TagChip";

//const DEFAULT_COLORS = [grey[100], grey[200], grey[300], grey[400], grey[500]];
const DEFAULT_COLORS = [grey[100], grey[300]];


function ContextMenu(props: { context: Context, setOpen: Opener }) {

    return (
        <PopupState variant="popover" popupId="demo-popup-menu">
            {(popupState) => (
                <>
                    <IconButton {...bindTrigger(popupState)}><MenuIcon /></IconButton>

                    <Menu {...bindMenu(popupState)}>

                        <MenuItem onClick={() => { props.setOpen(getAllChildren(props.context), OpenerMode.Open); popupState.close() }}>
                            <ListItemIcon>
                                <ArrowDropDownIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText>Expand all children</ListItemText>
                        </MenuItem>
                        <MenuItem onClick={() => { props.setOpen(getAllChildren(props.context), OpenerMode.Close); popupState.close() }}>
                            <ListItemIcon>
                                <ArrowRightIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText>Collapse all children</ListItemText>
                        </MenuItem>
                    </Menu>
                </>
            )}
        </PopupState>
    );
}

export function ContextNode(props: { context: Context, depth: number, opened: Set<string>, setOpen: Opener }) {
    //let [open, setOpen] = useState<boolean>(props.depth < 1);

    let c = props.context;
    let open = props.opened.has(c.uid);
    //let depth = props.depth <= 4 ? props.depth : 4;
    //if (props.context.meta)
    let colorBackground = c.meta?.color_bg;
    if (!colorBackground) {
        colorBackground = DEFAULT_COLORS[props.depth % 2];
    }

    let borderColor = c.meta?.color;
    let border = borderColor ? 5 : undefined;
    let color = c.meta?.color_text;

    let icon;

    if (c.state === "open") {
        icon = <span style={{ paddingRight: 10 }}><CircularProgress size="1em" /></span>
    } else if (c.state === "event") {
        icon = <CircleIcon style={{ paddingRight: 10 }} />
    } else if (c.state === "error") {
        icon = <ErrorIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "repeat_on_failure") {
        icon = <ReplayIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "query") {
        icon = <QuestionMarkIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "action") {
        icon = <ForwardIcon style={{ paddingRight: 10 }} />
    } else if (c.kind === "observation") {
        icon = <VisibilityIcon style={{ paddingRight: 10 }} />
    } else {
        icon = <AccountTreeIcon style={{ paddingRight: 10 }} />
    }

    function body() {
        return <>
            {(c.inputs || c.result || c.error) && <Divider />}
            {c.inputs && <p>
                <strong>Inputs</strong><br />
                <DataRenderer uid={c.uid + "/inputs"} data={c.inputs} opened={props.opened} setOpen={props.setOpen} />
            </p>}
            {c.children?.filter((ctx) => !ctx.kind || props.opened.has(ctx.kind)).map((ctx) => <div key={ctx.uid} style={{ paddingLeft: 15 }}>
                <ContextNode context={ctx} depth={props.depth + 1} opened={props.opened} setOpen={props.setOpen} /></div>)}
            {c.result &&
                <p>
                    <strong>Result</strong><br />
                    <DataRenderer uid={c.uid + "/result"} data={c.result} opened={props.opened} setOpen={props.setOpen} />
                </p>
            }
            {c.error &&
                <p>
                    <strong>Error</strong><br />
                    <DataRenderer uid={c.uid + "/error"} data={c.error} hideType="error" opened={props.opened} setOpen={props.setOpen} />
                </p>
            }
        </>
    }

    let short_result = c.result ? short_repr(c.result) : null;
    const dur = duration(props.context);
    if (dur && dur > 0) {
        <span style={{ color: "gray", marginLeft: 10 }}>{humanReadableDuration(dur)}</span>
    }

    return <Item sx={{ border, borderColor, color }} style={{ backgroundColor: colorBackground }} variant="outlined">

        <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
        }}>
            <IconButton onClick={() => props.setOpen(c.uid, OpenerMode.Toggle)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>{icon}
            {c.name} {short_result && <><ArrowRightAltIcon /> {short_result}</>} {c.kind ? " [" + c.kind + "]" : ""}
            {dur && dur > 0 ? <span style={{ color: "gray", marginLeft: 10 }}>{humanReadableDuration(dur)}</span> : ""}
            <ContextMenu context={c} setOpen={props.setOpen} />
            {c.tags?.map((t, i) => <TagChip key={i} tag={t} />)}
        </div>
        {open && body()}
    </Item >
}