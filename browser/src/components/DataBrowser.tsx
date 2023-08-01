import { Box, CircularProgress, Divider, IconButton, ListItemButton, ListItemText, Paper, Switch, Tooltip } from "@mui/material";
import { Context, gatherKindsAndTags, getContextAge } from "../model/Context";
import { ContextNode } from "./ContextNode";
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";
import ToggleButton from '@mui/material/ToggleButton';

import SyncIcon from '@mui/icons-material/Sync';
import DoneIcon from '@mui/icons-material/Done';
import ErrorIcon from '@mui/icons-material/Error';
import { TagChip } from "./TagChip";
import DeleteIcon from '@mui/icons-material/Delete';
import { humanReadableDuration } from "../common/utils";
import { ContextDetailsDialog } from "./ContextDetails";
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import { ConfirmDialog } from "./ConfirmDialog";


type RootsVisibility = {
    showFinished: boolean,
    showFailed: boolean,
}


export type BrowserConfig = {
    themeWithBoxes: boolean
}

export enum OpenerMode {
    Toggle,
    Open,
    Close
}

export type Opener = (keys: string | string[], mode: OpenerMode) => void


export type BrowserEnv = {
    config: BrowserConfig,
    opened: Set<string>,
    setOpen: Opener,
    showContextDetails: (ctx: Context) => void,
}



function RootItem(props: { root: Context, selectedCtx: Context | null, selectRoot: (uid: string) => void }) {
    const { root, selectedCtx, selectRoot } = props;
    let primary = root.uid.slice(0, 40);

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

    const age = getContextAge(root);

    return (
        <ListItemButton selected={selectedCtx !== null && root.uid === selectedCtx.uid} key={root.uid} component="a" onClick={() => selectRoot(root.uid)}>
            {icon}
            <ListItemText primaryTypographyProps={{ fontSize: '80%', color: color }}>
                <div>{primary}</div>
                <div>{age && <span style={{ color: "gray" }}>{humanReadableDuration(age)} ago</span>} {root.tags?.map((t, i) => <TagChip key={i} tag={t} />)}</div>
            </ListItemText>
        </ListItemButton>
    )
}

function RootPanel(props: { roots: Context[], selectedCtx: Context | null, selectRoot: (ctx: string) => void, showRoots: RootsVisibility, setShowRoots: (v: RootsVisibility) => void, refresh: () => void, addInfo: AddInfo }) {
    const [confirmDialog, setConfirmDialog] = useState<boolean>(false);

    const showRoots = props.showRoots;


    function filterStates(ctx: Context) {
        if (!showRoots.showFinished && ctx.state === undefined) {
            return false;
        }
        if (!showRoots.showFailed && ctx.state === "error") {
            return false;
        }
        return true;
    }

    function copyIntoClipboard() {
        if (props.selectedCtx) {
            navigator.clipboard.writeText(props.selectedCtx.uid);
            props.addInfo("success", `Context uid '${props.selectedCtx.uid} copied into clipboard`)
        }
    }

    function onDelete(confirmed: boolean) {
        setConfirmDialog(false);
        if (confirmed) {
            callGuard(async () => {
                if (props.selectedCtx) {
                    await axios.delete(SERVICE_PREFIX + "/contexts/uid/" + props.selectedCtx.uid);
                    props.refresh();
                }
            }, props.addInfo)

        }
    }

    return <div style={{ width: 360, float: "left" }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>
                <Tooltip title="Show/Hide finished contexts">
                    <ToggleButton
                        size="small"
                        value="check"
                        selected={showRoots.showFinished}
                        onChange={(e) => {
                            props.setShowRoots({ ...showRoots, showFinished: !showRoots.showFinished })
                        }}
                    >
                        <DoneIcon />
                    </ToggleButton>
                </Tooltip>
                <Tooltip title="Show/Hide failed contexts">
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
            </span>
            <span>
                <IconButton onClick={() => setConfirmDialog(true)}><DeleteIcon /></IconButton>
                <IconButton onClick={copyIntoClipboard}><ContentPasteIcon /></IconButton>
                <IconButton onClick={props.refresh}><SyncIcon /></IconButton>
            </span>
        </div>
        <Divider style={{ marginBottom: 5, marginTop: 5 }} />
        <Paper style={{ maxHeight: "calc(100vh - 40px)", overflow: 'auto' }}>
            {props.roots.filter(filterStates).map((root) => <RootItem key={root.uid} root={root} selectedCtx={props.selectedCtx} selectRoot={props.selectRoot} />
            )}
        </Paper>

        {props.selectedCtx && <ConfirmDialog open={confirmDialog} confirmText={"Remove context"} onConfirm={onDelete}>
            Remove context <strong>{props.selectedCtx.uid}</strong>?
        </ConfirmDialog>}
    </div >

}



export function DataBrowser(props: { addInfo: AddInfo }) {
    const [config, setConfig] = useState<BrowserConfig>({ themeWithBoxes: false });
    const [roots, setRoots] = useState<Context[]>([]);
    const [selectedCtx, setSelectedCtx] = useState<Context | null>(null);
    let [opened, setOpened] = useState<Set<string>>(new Set());
    const [kinds, setKinds] = useState<Set<string>>(new Set());
    const [ctxDetails, setCtxDetails] = useState<Context | null>(null);
    const [showRoots, setShowRoots] = useState<RootsVisibility>({ showFinished: true, showFailed: true });


    function refresh() {
        callGuard(async () => {
            const response1 = await axios.get(SERVICE_PREFIX + "/contexts/list");
            if (response1 === null) {
                return;
            }
            const uids = response1.data as string[];

            const forget_open = roots.filter(c => c.state !== 'open');
            const local_uids = new Set(forget_open.map(c => c.uid));
            const to_download: string[] = [];
            for (const uid of uids) {
                if (!local_uids.has(uid)) {
                    to_download.push(uid);
                }
            }
            const response2 = await axios.post(SERVICE_PREFIX + "/contexts/roots", { "uids": to_download });
            if (response2 === null) {
                return;
            }
            const new_roots = response2.data as Context[];
            const uids_set = new Set(uids);

            const final_roots = forget_open.filter((c) => uids_set.has(c.uid)).concat(new_roots);
            final_roots.sort()

            final_roots.sort((a, b) => {
                if (a.start_time && b.start_time) {
                    if (a.start_time < b.start_time) {
                        return 1;
                    }
                    if (a.start_time > b.start_time) {
                        return -1;
                    }
                }
                return 0;
            });

            setRoots(final_roots);

            if (selectedCtx === null && final_roots.length > 0) {
                selectRoot(final_roots[0].uid);
            } else if (selectedCtx !== null && final_roots.find((x) => x.uid === selectedCtx.uid)) {
                selectRoot(selectedCtx.uid);
            } else {
                setSelectedCtx(null);
            }
        }, props.addInfo);
    }

    function selectRoot(root: string) {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/uid/" + root);
            const ctx = response.data as Context;
            setSelectedCtx(ctx);
            setOpened((op) => {
                let o = new Set(op);
                o.add(root);
                if (newKinds.size !== kinds.size) {
                    newKinds.forEach((k) => {
                        if (!kinds.has(k)) {
                            o.add(k);
                        }
                    })
                }
                return o;
            })
            const newKinds = new Set(kinds);
            gatherKindsAndTags(ctx, newKinds);
            if (newKinds.size !== kinds.size) {
                setKinds(newKinds);
            }
        }, props.addInfo)
    }

    function setOpen(keys: string | string[], mode: OpenerMode) {
        setOpened((op) => {
            let o = new Set(op);
            if (!Array.isArray(keys)) {
                keys = [keys]
            }
            if (mode === OpenerMode.Toggle) {
                for (const key of keys) {
                    if (!o.delete(key)) {
                        o.add(key)
                    }
                }
            } else if (mode === OpenerMode.Open) {
                for (const key of keys) {
                    o.add(key)
                }
            } else {
                for (const key of keys) {
                    o.delete(key)
                }
            }
            return o;
        })

    }

    let sortedKinds = Array.from(kinds);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { refresh() }, []);

    const env: BrowserEnv = {
        config,
        opened,
        setOpen,
        showContextDetails: setCtxDetails
    }

    return <div>
        <RootPanel showRoots={showRoots} setShowRoots={setShowRoots} roots={roots} selectedCtx={selectedCtx} refresh={refresh} selectRoot={selectRoot} addInfo={props.addInfo} />
        <div style={{ float: "left", width: "calc(100% - 365px)", overflow: 'auto' }}>
            <Box
                m={1} //margin
                display="flex"
                justifyContent="flex-start"
                alignItems="flex-start"
            >
                <Switch
                    checked={config.themeWithBoxes}
                    onChange={(e) => setConfig({ ...config, themeWithBoxes: e.target.checked })}
                />
                {sortedKinds.map((kind) => <ToggleButton sx={{ paddingTop: 0.2, paddingBottom: 0.2, marginLeft: 0.5 }} value={""} selected={opened.has(kind)} onChange={() => setOpen(kind, OpenerMode.Toggle)} key={kind}>{kind}</ToggleButton>)}
            </Box>
            {selectedCtx && <div style={{ maxHeight: "calc(100vh - 70px)", overflow: 'auto' }}><ContextNode env={env} context={selectedCtx} depth={0} /></div>}
            {roots.length === 0 && !selectedCtx && <span>No context registed in Data Browser</span>}
        </div>
        {ctxDetails && <ContextDetailsDialog context={ctxDetails} onClose={() => setCtxDetails(null)} />}
    </div >
}