// Supabase Edge Function: /wells
// Handles CRUD operations for wells via Supabase database.
// Deploy with: supabase functions deploy wells

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
  // Extract well id from path: /wells/:id
  const pathParts = url.pathname.split("/").filter(Boolean);
  const wellId = pathParts[pathParts.length - 1] !== "wells" ? pathParts[pathParts.length - 1] : null;

  try {
    if (req.method === "GET") {
      const {data, error} = await supabase.from("wells").select("*").order("well_number");

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: {...corsHeaders, "Content-Type": "application/json"},
        status: 200,
      });
    }

    if (req.method === "PUT" && wellId) {
      const body = await req.json();
      const {data, error} = await supabase
        .from("wells")
        .update(body)
        .eq("id", wellId)
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
