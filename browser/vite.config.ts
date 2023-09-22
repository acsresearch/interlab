import { defineConfig } from 'vite'
import { resolve } from 'path'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    /*build: {
        rollupOptions: {
            input: {
                single: resolve(__dirname, 'src/SingleContextView.tsx'),
            },
            output: {
                format: "iife",
                name: "interlab",
                globals: {
                    react: "React",
                    "react-dom": "ReactDOM"
                }
            }
        },
    },*/
})
