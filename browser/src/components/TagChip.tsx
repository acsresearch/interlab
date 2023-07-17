import { Chip } from "@mui/material";
import { Tag } from "../model/Context";

export function TagChip(props: { tag: string | Tag }) {
    let tag;
    if (typeof props.tag === 'string') {
        tag = { name: props.tag }
    } else {
        tag = props.tag;
    }
    return <Chip label={tag.name} sx={{ backgroundColor: tag.color }} size="small" />
}