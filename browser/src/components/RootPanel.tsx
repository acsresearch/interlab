import { Box, CircularProgress, Divider, IconButton, ListItemButton, ListItemText, Menu, MenuItem, Paper, Tooltip } from "@mui/material";
import { TracingNode, Tag, collectTags, getNodeAge, hasTag } from "../model/TracingNode";
import { useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";
import ToggleButton from '@mui/material/ToggleButton';

import SyncIcon from '@mui/icons-material/Sync';
import DoneIcon from '@mui/icons-material/Done';
import SellIcon from '@mui/icons-material/Sell';
import ErrorIcon from '@mui/icons-material/Error';
import { TagChip } from "./TagChip";
import DeleteIcon from '@mui/icons-material/Delete';
import { humanReadableDuration } from "../common/utils";
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import { ConfirmDialog } from "./ConfirmDialog";
import PopupState, { bindMenu, bindTrigger } from "material-ui-popup-state";


export type RootsVisibility = {
    showFinished: boolean,
    showFailed: boolean,
}



function RootItem(props: { root: TracingNode, selectedCtx: TracingNode | null, selectRoot: (uid: string) => void }) {
    const { root, selectedCtx, selectRoot } = props;
    const primary = root.uid.slice(0, 40);

    let icon;
    let color;

    if (root.state === "open") {
        icon = <span style={{ paddingRight: 5 }}><CircularProgress size="1em" /></span>;
        color = "green";
    } else if (root.state === "error") {
        icon = <ErrorIcon sx={{ fontSize: "110%", marginRight: 0.5, color: "red" }} />
        color = "red";
    } else {
        icon = <DoneIcon sx={{ fontSize: "110%", paddingRight: 0.5 }} />
    }

    const age = getNodeAge(root);

    return (
        <ListItemButton selected={selectedCtx !== null && root.uid === selectedCtx.uid} key={root.uid} component="a" onClick={() => selectRoot(root.uid)}>
            {icon}
            <ListItemText primaryTypographyProps={{ fontSize: '80%', color: color }}>
                <Box>{primary}</Box>
                <Box>{age && <span style={{ color: "gray" }}>{humanReadableDuration(age)} ago</span>} {root.tags?.map((t, i) => <TagChip key={i} tag={t} size="small" />)}</Box>
            </ListItemText>
        </ListItemButton>
    )
}

export function FilterByTagButton(props: { roots: TracingNode[], tagFilters: Tag[], onClick: (tag: Tag) => void }) {
    return <PopupState variant="popover">
        {(popupState) => {
            const tags = popupState.isOpen ? collectTags(props.roots).filter(tag => !props.tagFilters.find(t => t.name === tag.name)) : [];
            return (<>
                <IconButton {...bindTrigger(popupState)}><SellIcon /></IconButton>
                <Menu {...bindMenu(popupState)}>
                    {tags.map((tag, i) => <MenuItem key={i} onClick={() => { props.onClick(tag); popupState.close() }}><TagChip tag={tag} /></MenuItem>)}
                </Menu>
            </>)
        }}
    </PopupState >
}

export function RootPanel(props: { roots: TracingNode[], selectedNode: TracingNode | null, selectRoot: (ctx: string) => void, showRoots: RootsVisibility, setShowRoots: (v: RootsVisibility) => void, refresh: () => void, addInfo: AddInfo }) {
    const [confirmDialog, setConfirmDialog] = useState<boolean>(false);
    const [tagFilters, setTagFilters] = useState<Tag[]>([]);

    const showRoots = props.showRoots;


    function filterRoots(ctx: TracingNode) {
        if (!showRoots.showFinished && ctx.state === undefined) {
            return false;
        }
        if (!showRoots.showFailed && ctx.state === "error") {
            return false;
        }
        if (tagFilters.length > 0 && !tagFilters.every(tag => hasTag(ctx, tag.name))) {
            return false;
        }
        return true;
    }

    function copyIntoClipboard() {
        if (props.selectedNode) {
            navigator.clipboard.writeText(props.selectedNode.uid);
            props.addInfo("success", `Node uid '${props.selectedNode.uid} copied into clipboard`)
        }
    }

    function onDelete(confirmed: boolean) {
        setConfirmDialog(false);
        if (confirmed) {
            callGuard(async () => {
                if (props.selectedNode) {
                    await axios.delete(SERVICE_PREFIX + "/nodes/uid/" + props.selectedNode.uid);
                    props.refresh();
                }
            }, props.addInfo)

        }
    }

    return <div style={{ width: 360, float: "left" }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>
                <Tooltip title="Show/Hide finished nodes">
                    <ToggleButton
                        size="small"
                        value="check"
                        selected={showRoots.showFinished}
                        onChange={() => {
                            props.setShowRoots({ ...showRoots, showFinished: !showRoots.showFinished })
                        }}
                    >
                        <DoneIcon />
                    </ToggleButton>
                </Tooltip>
                <Tooltip title="Show/Hide failed nodes">
                    <ToggleButton
                        size="small"
                        value="check"
                        selected={showRoots.showFailed}
                        onChange={() => {
                            props.setShowRoots({ ...showRoots, showFailed: !showRoots.showFailed })
                        }}
                    >
                        <ErrorIcon />
                    </ToggleButton>
                </Tooltip>
                <FilterByTagButton roots={props.roots} tagFilters={tagFilters} onClick={(tag) => setTagFilters([...tagFilters, tag])} />
            </span>
            <span>
                <IconButton onClick={() => setConfirmDialog(true)}><DeleteIcon /></IconButton>
                <IconButton onClick={copyIntoClipboard}><ContentPasteIcon /></IconButton>
                <IconButton onClick={props.refresh}><SyncIcon /></IconButton>
            </span>
        </div>
        <Divider style={{ marginBottom: 5, marginTop: 5 }} />
        {
            tagFilters.length > 0 && <>
                <Box>
                    {tagFilters.map(tag => <Box component="span" key={tag.name} sx={{ ml: 0.3, mr: 0.3 }}><TagChip tag={tag} onDelete={() => { setTagFilters(tagFilters.filter((t => t.name !== tag.name))) }} /></Box>)}
                </Box>
                <Divider style={{ marginBottom: 5, marginTop: 5 }} />
            </>
        }

        <Paper style={{ maxHeight: "calc(100vh - 40px)", overflow: 'auto' }}>
            {props.roots.filter(filterRoots).map((root) => <RootItem key={root.uid} root={root} selectedCtx={props.selectedNode} selectRoot={props.selectRoot} />
            )}
        </Paper>

        {
            props.selectedNode && <ConfirmDialog open={confirmDialog} confirmText={"Remove node"} onConfirm={onDelete}>
                Remove node <strong>{props.selectedNode.uid}</strong>?
            </ConfirmDialog>
        }
    </div >

}
