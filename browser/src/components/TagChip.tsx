import { Chip } from "@mui/material";
import { Tag } from "../model/TracingNode";

export function TagChip(props: { tag: string | Tag, onDelete?: () => void, size?: "small" }) {
    let tag;
    if (typeof props.tag === 'string') {
        tag = { name: props.tag }
    } else {
        tag = props.tag;
    }
    return <Chip label={tag.name} sx={{ backgroundColor: tag.color }} onDelete={props.onDelete} size={props.size} />
}