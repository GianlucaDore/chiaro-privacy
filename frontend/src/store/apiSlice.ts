/* // ESEMPIO DI USO DI RTK QUERY:

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'apiSlice',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://jsonplaceholder.typicode.com' }),
  endpoints: (builder) => ({
    // --------- QUERIES ---------
    getPosts: builder.query<Post[], void>({
      query: () => '/posts',
      providesTags: (result) =>
        result
          ? [
              // Tag generico della lista
              { type: 'Posts', id: 'LIST' },
              // Tag per ogni item
              ...result.map((p) => ({ type: 'Posts' as const, id: p.id })),
            ]
          : [{ type: 'Posts', id: 'LIST' }],
    }),

    // --------- MUTATIONS ---------
    createPost: builder.mutation<Post, CreatePostInput>({
      query: (payload) => ({
        url: '/create-post',
        method: 'POST',
        body: payload,
      }),
      // La creazione invalida la lista di posts fetchati: forza il refetch di getPosts
      invalidatesTags: [{ type: 'Posts', id: 'LIST' }],
    }),

});

export const { useGetPostsQuery, useCreatePost } = api;

*/