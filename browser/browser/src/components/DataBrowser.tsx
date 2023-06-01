import { Grid, IconButton, ListItemButton, ListItemText, Paper } from "@mui/material"
import { Context } from "../model/Context"
import { ContextNode } from "./ContextNode"
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";

import SyncIcon from '@mui/icons-material/Sync';

// type Root = {
//     name: string,
//     uuid: string,
// }


export function DataBrowser(props: { addInfo: AddInfo }) {
    const [roots, setRoots] = useState<string[]>([]);
    const [selectedCtx, setSelectedCtx] = useState<Context | null>(null);
    let [opened, setOpened] = useState<Set<string>>(new Set());

    function refresh() {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/list");
            if (response === null) {
                return;
            }
            const rs = response.data as string[];
            setRoots(rs);
            if (selectedCtx === null && rs.length > 0) {
                selectRoot(rs[0]);
            } else if (selectedCtx !== null && rs.find((x) => x === selectedCtx.uuid)) {
                selectRoot(selectedCtx.uuid);
            } else {
                setSelectedCtx(null);
            }
        }, props.addInfo);
    }

    function selectRoot(root: string) {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/uuid/" + root);
            const ctx = response.data as Context;
            setSelectedCtx(ctx);
            setOpened((op) => {
                let o = new Set(op);
                o.add(root);
                return o;
            })
        }, props.addInfo)
    }

    function toggleOpen(uuid: string) {
        setOpened((op) => {
            let o = new Set(op);
            if (!o.delete(uuid)) {
                o.add(uuid)
            }
            return o;
        })

    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { refresh() }, []);

    return <Grid container>
        <Grid item xs={2}>
            <IconButton onClick={refresh}><SyncIcon /></IconButton>
            <Paper>
                {roots.map((root) =>
                    <ListItemButton selected={selectedCtx !== null && root === selectedCtx.uuid} key={root} component="a" onClick={() => selectRoot(root)}>
                        <ListItemText primary={root.slice(0, 8)} />
                    </ListItemButton>
                )}
            </Paper>
        </Grid>
        <Grid item xs={9}>
            {selectedCtx && <ContextNode context={selectedCtx} depth={0} opened={opened} toggleOpen={toggleOpen} />}
            {roots.length === 0 && !selectedCtx && <span>No context registed in Data Browser</span>}
        </Grid>
    </Grid>
}