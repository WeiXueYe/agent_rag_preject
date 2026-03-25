import { createBrowserClient } from '@supabase/ssr'

const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
)

export default supabase


export type Agent = {
  id?: number;
  creater?: string;
  created_at?: string;
  agent_name: string;
  prompt: string;
};


export const createAgent = async () => {
  const { data, error } = await supabase.from('agent').insert({}).select()
  if (error) { 
    console.error(error)
    throw error
  }
  return data
}

export const getAgents = async () => {
  const { data: agents, error } = await supabase.from('agent').select()
  if (error) {
    console.error(error)
    throw error
  }
  return agents
}

export const updateAgent = async (agent: Agent) => {
  const { error } = await supabase.from('agent').update(agent).eq('id', agent.id)
  if (error) {
    console.error(error)
    throw error
  }
  return agent
}

export const deleteAgent = async (id: number) => {
  const { error } = await supabase.from('agent').delete().eq('id', id)
  if (error) {
    console.error(error)
    throw error
  }
  return id
}