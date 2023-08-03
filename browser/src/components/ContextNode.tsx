

import { Context, duration, getAllChildren } from "../model/Context";
import { Box, CircularProgress, IconButton, ListItemIcon, ListItemText, Menu, MenuItem, Stack, Typography } from "@mui/material";

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
import { BrowserEnv, OpenerMode } from "./DataBrowser";
import { TagChip } from "./TagChip";
import React from "react";

//const DEFAULT_COLORS = [grey[100], grey[200], grey[300], grey[400], grey[500]];
const DEFAULT_COLORS = [grey[100], grey[300]];


function ContextMenu(props: { context: Context, env: BrowserEnv }) {

    return (
        <PopupState variant="popover" popupId="demo-popup-menu">
            {(popupState) => (
                <>
                    <IconButton {...bindTrigger(popupState)}><MenuIcon /></IconButton>

                    <Menu {...bindMenu(popupState)}>

                        <MenuItem onClick={() => { props.env.setOpen(getAllChildren(props.context), OpenerMode.Open); popupState.close() }}>
                            <ListItemIcon>
                                <ArrowDropDownIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText>Expand all children</ListItemText>
                        </MenuItem>
                        <MenuItem onClick={() => { props.env.setOpen(getAllChildren(props.context), OpenerMode.Close); popupState.close() }}>
                            <ListItemIcon>
                                <ArrowRightIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText>Collapse all children</ListItemText>
                        </MenuItem>
                        <MenuItem onClick={() => { props.env.showContextDetails(props.context); popupState.close() }}>
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

function ContextNodeItem(props: { icon: React.ReactNode, children?: React.ReactNode }) {
    return <Stack direction="row" sx={{ ml: 2, mt: 1, mb: 1, }}>
        {props.icon}
        <Box sx={{ ml: 1 }}>{props.children}</Box>
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

    let iconStyle = { pr: 0.5, color: mainColor };

    if (c.state === "open") {
        icon = <Box component="span" sx={{ pr: 0.5 }}><CircularProgress size="1em" /></Box>
    } else if (c.state === "event") {
        icon = <CircleIcon sx={iconStyle} />
    } else if (c.state === "error") {
        icon = <ErrorIcon sx={iconStyle} />
    } else if (c.kind === "repeat_on_failure") {
        icon = <ReplayIcon sx={iconStyle} />
    } else if (c.kind === "query") {
        icon = <QuestionMarkIcon sx={iconStyle} />
    } else if (c.kind === "action") {
        icon = <GamepadIcon sx={iconStyle} />
    } else if (c.kind === "observation") {
        icon = <VisibilityIcon sx={iconStyle} fontSize="small" />
        small = true;
    } else {
        icon = <AccountTreeIcon sx={iconStyle} />
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

        return <Box sx={{ borderLeft, textAlign: "left", ml: 5.7 }}>
            {inputs &&
                (
                    inputs.map(({ property, value }, i) =>

                        <ContextNodeItem key={i} icon={<ArrowForwardIcon />}>
                            <Box><strong>{property}</strong></Box>
                            <DataRenderer uid={c.uid + "/inputs/" + property} data={value} env={props.env} />
                        </ContextNodeItem>
                    )

                )
            }
            {
                c.children && (
                    <Box sx={{ ml: 1, mt: 1, mb: 1, }}>
                        {c.children?.filter(isVisible).map((ctx) =>
                            <ContextNode key={ctx.uid} env={props.env} context={ctx} depth={props.depth + 1} />)}
                    </Box>
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
        </Box>
    }

    const header = () => {
        let short_result = undefined; // c.result ? short_repr(c.result) : null;
        const dur = duration(props.context);
        return <Box sx={{ display: "flex", alignContent: "space-between" }}>
            <Box style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                width: "100%",
            }}>
                <IconButton size="small" onClick={() => props.env.setOpen(c.uid, OpenerMode.Toggle)}>{open ? <ArrowDropDownIcon /> : <ArrowRightIcon />}</IconButton>{icon}
                <Box component="span" sx={{ color: mainColor, fontSize: small ? "75%" : undefined }}>{c.name}</Box> {short_result && <><ArrowRightAltIcon /> {short_result}</>} {/*c.kind ? " [" + c.kind + "]" : ""*/}
                {dur && dur > 0 ? <Box component="span" sx={{ color: "#999", marginLeft: 1 }}>{humanReadableDuration(dur)}</Box> : ""}
                {c.tags?.map((t, i) => <Box component="span" sx={{ marginLeft: 0.5 }} key={i}><TagChip tag={t} /></Box>)}
            </Box>
            <ContextMenu context={c} env={props.env} />
        </Box>
    }

    if (themeWithBoxes) {
        return <Item sx={{ backgroundColor, paddingTop: small ? 0 : undefined, paddingBottom: small ? 0 : undefined, border: borderColor ? `2px ${borderColor} solid` : undefined }}>
            <>
                {header()}
                {open && body()}
            </>
        </Item >
    } else {
        return <Box sx={{ backgroundColor, border: borderColor ? `2px ${borderColor} solid` : undefined }}>
            <Typography color="text.secondary">
                {header()}
                {open && body()}
            </Typography>
        </Box>
    }
}