// Supabase Edge Function: /repairs
// Handles CRUD operations for well repairs via Supabase database.
// Supports optional filtering by well_id query parameter.
// Deploy with: supabase functions deploy repairs

import {createClient} from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
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

  const url = new URL(req.url);
  const wellId = url.searchParams.get("well_id");
  // Extract repair id from path: /repairs/:id
  const pathParts = url.pathname.split("/").filter(Boolean);
  const repairId =
    pathParts[pathParts.length - 1] !== "repairs" ? pathParts[pathParts.length - 1] : null;

  try {
    if (req.method === "GET") {
      let query = supabase.from("repairs").select("*").order("start_date", {ascending: false});

      if (wellId) {
        query = query.eq("well_id", wellId);
      }

      const {data, error} = await query;

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: {...corsHeaders, "Content-Type": "application/json"},
        status: 200,
      });
    }

    if (req.method === "PUT" && repairId) {
      const body = await req.json();
      const {data, error} = await supabase
        .from("repairs")
        .update(body)
        .eq("id", repairId)
        .select()
        .single();

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
