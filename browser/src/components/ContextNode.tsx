

import { Context, duration, getAllChildren } from "../model/Context";
import { CircularProgress, IconButton, ListItemIcon, ListItemText, Menu, MenuItem, Stack, Typography } from "@mui/material";

import { grey } from '@mui/material/colors';
import { Item } from "./Item";
import { DataRenderer } from "./DataRenderer";

import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ReplayIcon from '@mui/icons-material/Replay';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import ErrorIcon from '@mui/icons-material/Error';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import VisibilityIcon from '@mui/icons-material/Visibility';
import MenuIcon from '@mui/icons-material/Menu';
import CircleIcon from '@mui/icons-material/Circle';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import GamepadIcon from '@mui/icons-material/Gamepad';
import DataObjectIcon from '@mui/icons-material/DataObject';

import { humanReadableDuration } from "../common/utils";
import PopupState, { bindMenu, bindTrigger } from "material-ui-popup-state";
import { BrowserEnv, Opener, OpenerMode } from "./DataBrowser";
import { TagChip } from "./TagChip";
import React from "react";

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
                        <MenuItem onClick={() => { props.setOpen(getAllChildren(props.context), OpenerMode.Close); popupState.close() }}>
                            <ListItemIcon>
                                <DataObjectIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText>Show JSON</ListItemText>
                        </MenuItem>
                    </Menu>
                </>
            )}
        </PopupState>
    );
}

function ContextNodeItem(props: { icon?: React.ReactNode, title?: string, children?: React.ReactNode }) {
    return <Stack direction="row" style={{ marginLeft: 20, marginTop: 5, marginBottom: 5, }}>
        {props.icon}
        <div style={{ marginLeft: 10 }}>{props.children}</div>
    </Stack>
}


export function ContextNode(props: { env: BrowserEnv, context: Context, depth: number }) {
    const themeWithBoxes = props.env.config.themeWithBoxes;

    let c = props.context;
    let open = props.env.opened.has(c.uid);
    let backgroundColor = c.meta?.color_bg;
    if (!backgroundColor && themeWithBoxes) {
        backgroundColor = DEFAULT_COLORS[props.depth % 2];
    }

    let mainColor = c.meta?.color;

    // HACK =========
    // if (mainColor === "#ffb27f50") {
    //     mainColor = "red";
    // }

    // if (mainColor === "#ff9a7f50") {
    //     mainColor = "green";
    // }
    // ===============


    let icon: React.ReactNode;
    let small = false;

    let iconStyle = { paddingRight: 10, color: mainColor };

    if (c.state === "open") {
        icon = <span style={{ paddingRight: 10 }}><CircularProgress size="1em" /></span>
    } else if (c.state === "event") {
        icon = <CircleIcon style={iconStyle} />
    } else if (c.state === "error") {
        icon = <ErrorIcon style={iconStyle} />
    } else if (c.kind === "repeat_on_failure") {
        icon = <ReplayIcon style={iconStyle} />
    } else if (c.kind === "query") {
        icon = <QuestionMarkIcon style={iconStyle} />
    } else if (c.kind === "action") {
        icon = <GamepadIcon style={iconStyle} />
    } else if (c.kind === "observation") {
        icon = <VisibilityIcon style={iconStyle} fontSize="small" />
        small = true;
    } else {
        icon = <AccountTreeIcon style={iconStyle} />
    }

    const borderColor = c.meta?.color_border;

    function isVisible(ctx: Context) {
        if (ctx.kind) {
            if (!props.env.opened.has(ctx.kind)) {
                return false;
            }
        }
        if (ctx.tags) {
            return ctx.tags.every((tag) => {
                if (typeof tag === 'string') {
                    return props.env.opened.has(tag)
                } else {
                    return props.env.opened.has(tag.name)
                }
            })
        }
        return true;
    }

    function body() {
        let inputs;

        if (c.inputs) {
            inputs = [];
            for (const property in c.inputs) {
                const value = c.inputs[property];
                inputs.push({ property, value });
            }
        }

        let borderLeft;
        if (!themeWithBoxes) {
            borderLeft = "1.5px " + (mainColor || "#666") + " solid"
        }

        return <div style={{ borderLeft, textAlign: "left", marginLeft: "45px" }}>
            {inputs &&
                (
                    inputs.map(({ property, value }, i) =>

                        <ContextNodeItem key={i} icon={<ArrowForwardIcon />}>
                            <div><strong>{property}</strong></div>
                            <DataRenderer uid={c.uid + "/inputs/" + property} data={value} env={props.env} />
                        </ContextNodeItem>
                    )

                )
            }
            {
                c.children && (
                    c.children?.filter(isVisible).map((ctx) => <div key={ctx.uid} style={{ paddingLeft: 5 }}>
                        <ContextNode env={props.env} context={ctx} depth={props.depth + 1} /></div>)
                )
            }
            {
                c.result &&
                <ContextNodeItem icon={<ArrowBackIcon />}>
                    <DataRenderer uid={c.uid + "/result"} data={c.result} env={props.env} />
                </ContextNodeItem>
            }
            {
                c.error &&
                <ContextNodeItem icon={<ReportProblemIcon />}>
                    <DataRenderer uid={c.uid + "/error"} data={c.error} hideType="error" env={props.env} />
                </ContextNodeItem>
            }
        </div >
    }

    const header = () => {
        let short_result = undefined; // c.result ? short_repr(c.result) : null;
        const dur = duration(props.context);
        if (dur && dur > 0) {
            <span style={{ color: "gray", marginLeft: 10 }}>{humanReadableDuration(dur)}</span>
        }
        return <div style={{ display: "flex", alignContent: "space-between" }}><div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            width: "100%",
        }}>
            <IconButton size="small" onClick={() => props.env.setOpen(c.uid, OpenerMode.Toggle)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>{icon}
            <span style={{ color: mainColor, fontSize: small ? "75%" : undefined }}>{c.name}</span> {short_result && <><ArrowRightAltIcon /> {short_result}</>} {/*c.kind ? " [" + c.kind + "]" : ""*/}
            {dur && dur > 0 ? <span style={{ color: "gray", marginLeft: 10 }}>{humanReadableDuration(dur)}</span> : ""}
            {c.tags?.map((t, i) => <span style={{ marginLeft: 5 }} key={i}><TagChip tag={t} /></span>)}
        </div>
            <ContextMenu context={c} setOpen={props.env.setOpen} />
        </div>
    }

    if (themeWithBoxes) {
        return <Item style={{ backgroundColor, paddingTop: small ? 0 : undefined, paddingBottom: small ? 0 : undefined, border: borderColor ? `2px ${borderColor} solid` : undefined }}>
            <>
                {header()}
                {open && body()}
            </>
        </Item >
    } else {
        return <div style={{ backgroundColor, border: borderColor ? `2px ${borderColor} solid` : undefined }}>
            <Typography color="text.secondary">
                {header()}
                {open && body()}
            </Typography>
        </div>
    }
}