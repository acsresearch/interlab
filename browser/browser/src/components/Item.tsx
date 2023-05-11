import { Paper } from "@mui/material";
import { styled } from "@mui/material/styles";

export const Item = styled(Paper)(({ theme }) => ({
    backgroundColor: '#fff',
    ...theme.typography.body2,
    padding: theme.spacing(1),
    marginBottom: theme.spacing(1),
    textAlign: 'left',
    color: theme.palette.text.secondary,
}));