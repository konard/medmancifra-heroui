// Supabase Edge Function: /fields
// Handles read operations for oil fields (drill site locations) via Supabase database.
// Deploy with: supabase functions deploy fields

import {createClient} from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Origin": "*",
};

Deno.serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {headers: corsHeaders});
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
  );

  try {
    if (req.method === "GET") {
      const {data, error} = await supabase.from("fields").select("*").order("name");

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: {...corsHeaders, "Content-Type": "application/json"},
        status: 200,
      });
    }

    return new Response(JSON.stringify({error: "Method not allowed"}), {
      headers: {...corsHeaders, "Content-Type": "application/json"},
      status: 405,
    });
  } catch (error) {
    return new Response(JSON.stringify({error: (error as Error).message}), {
      headers: {...corsHeaders, "Content-Type": "application/json"},
      status: 500,
    });
  }
});
