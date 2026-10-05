import { createClient } from '@supabase/supabase-js'

// In Vite, frontend environment variables are accessed with import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Create and export the Supabase client so any component in our app can use it
export const supabase = createClient(supabaseUrl, supabaseAnonKey)
