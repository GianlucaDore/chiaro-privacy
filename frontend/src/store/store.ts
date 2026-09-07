import { configureStore } from '@reduxjs/toolkit';
// import { genericReducer } from './store/genericSlice'
// import { apiSlice } from './store/apiSlice'
import { setupListeners } from '@reduxjs/toolkit/query';

export const store = configureStore({
  reducer: {
    // generic: genericReducer,

    // RTK Query:
    // [apiSlice.reducerPath]: apiSlice.reducer
  },
  /* middleware: (getDefaultMiddleware) => {
    // getDefaultMiddleware().concat(apiSlice.middleware)
    // ... Altri middleware custom vanno inseriti qui
  } */
})

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;