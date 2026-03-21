import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Settings, 
  User, 
  Terminal, 
  Link as LinkIcon, 
  Github, 
  CheckCircle2, 
  Circle, 
  ChevronRight,
  Database,
  Search,
  BookOpen,
  Layout,
  Cpu
} from 'lucide-react';

// --- Sub-Components ---

const Background = () => (
  <div className="fixed inset-0 -z-10 bg-bg-dark overflow-hidden">
    <div className="absolute top-1/4 -right-1/4 w-1/2 h-1/2 bg-brand-green/10 blur-[120px] rounded-full animate-pulse" />
    <div className="absolute -bottom-1/4 -left-1/4 w-1/2 h-1/2 bg-brand-blue/10 blur-[120px] rounded-full animate-pulse delay-700" />
    <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
  </div>
);

const RepoCard = ({ name, description, category }) => (
  <div className="group relative glass p-4 rounded-xl border-white/5 hover:border-brand-green/30 transition-all duration-300">
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-white/5 text-brand-green">
          <LinkIcon size={18} />
        </div>
        <div>
          <h4 className="font-bold text-brand-green text-sm group-hover:underline cursor-pointer">{name}</h4>
          <p className="text-xs text-white/50 mt-1 leading-relaxed">{description}</p>
        </div>
      </div>
      <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-1 rounded bg-white/5 text-white/40 border border-white/5">
        {category}
      </span>
    </div>
  </div>
);

const Message = ({ type, content, repos = [] }) => {
  const isAI = type === 'ai';
  return (
    <div className={`flex w-full mb-8 ${isAI ? 'justify-start' : 'justify-end'}`}>
      <div className={`flex gap-4 max-w-[85%] ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-lg ${
          isAI ? 'bg-brand-green text-bg-dark' : 'bg-brand-blue text-white'
        }`}>
          {isAI ? <Cpu size={18} /> : <User size={18} />}
        </div>
        
        <div className="flex flex-col gap-3">
          <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
            isAI ? 'glass text-white/90 border-white/5' : 'bg-brand-blue/10 border border-brand-blue/30 text-white'
          }`}>
            {content}
          </div>
          
          {repos.length > 0 && (
            <div className="grid gap-3 mt-1">
              <span className="text-[10px] font-mono uppercase tracking-widest text-white/30 flex items-center gap-2">
                <Database size={12} /> Recommended Repositories
              </span>
              {repos.map((repo, idx) => (
                <RepoCard key={idx} {...repo} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SidebarItem = ({ title, description, completed }) => (
  <div className="flex gap-4 group cursor-pointer py-3 border-b border-white/5 last:border-0 hover:bg-white/[0.02] px-2 rounded-lg transition-colors">
    <div className={`mt-1 shrink-0 ${completed ? 'text-brand-green' : 'text-white/20'}`}>
      {completed ? <CheckCircle2 size={18} /> : <Circle size={18} />}
    </div>
    <div className="flex flex-col gap-1">
      <h5 className={`text-xs font-bold ${completed ? 'text-white/90' : 'text-white/40'}`}>{title}</h5>
      <p className="text-[10px] text-white/30 line-clamp-1">{description}</p>
    </div>
  </div>
);

// --- Main App ---

export default function App() {
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      content: "Welcome to RepoHunter Coordinator. I am connected to your Llama-3 brain. How can I assist you with repository discovery today?",
      repos: []
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('roadmap');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { type: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: inputValue })
      });

      if (!response.ok) throw new Error('Failed to connect to RepoHunter Brain');

      const data = await response.json();
      
      // Basic parser for repos in the response (optional but nice)
      // For now, display the raw response content as an AI message
      setMessages(prev => [...prev, {
        type: 'ai',
        content: data.response,
        repos: [] // We can add a parser later to extract repo names for cards
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: `⚠️ Connection Error: ${error.message}. Please check if the local Hybrid Bridge (server.py) and Cloud Expert are online.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center p-6 text-white overflow-hidden">
      <Background />
      
      {/* Dynamic Header */}
      <header className="w-full max-w-7xl flex items-center justify-between mb-6 px-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute inset-0 bg-brand-green blur-md opacity-20" />
            <div className="w-10 h-10 bg-brand-green rounded-xl flex items-center justify-center text-bg-dark relative z-10">
              <Terminal size={24} />
            </div>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">RepoHunter <span className="text-white/30 font-medium text-sm ml-1">v2.4.0</span></h1>
            <p className="text-[10px] text-brand-green font-mono uppercase tracking-widest">Universal Matchmaker</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer text-white/40 hover:text-white transition-colors">
            <Settings size={18} />
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-blue to-purple-600 border border-white/20 shadow-lg shadow-brand-blue/20" />
        </div>
      </header>

      {/* Main Container */}
      <main className="w-full max-w-7xl flex-1 flex gap-6 overflow-hidden">
        
        {/* Chat Section */}
        <section className="flex-1 glass-morphism flex flex-col overflow-hidden relative border-white/10 shadow-2xl">
          <div className="flex-1 overflow-y-auto p-8 pt-12 custom-scrollbar">
            {messages.map((m, idx) => <Message key={idx} {...m} />)}
            {isLoading && (
              <div className="flex justify-start mb-8 animate-pulse">
                <div className="w-8 h-8 rounded-lg bg-brand-green/20 flex items-center justify-center text-brand-green">
                  <Cpu size={18} className="animate-spin" />
                </div>
                <div className="ml-4 glass p-4 rounded-2xl text-xs text-white/40 italic">
                  RepoHunter is searching your 50k repo database...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-6 border-t border-white/5 bg-white/[0.01]">
            <div className="relative flex items-center">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                disabled={isLoading}
                placeholder="Ask Tech Coordinator a question..." 
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:border-brand-green/50 transition-all placeholder:text-white/20 disabled:opacity-50"
              />
              <button 
                onClick={handleSend}
                disabled={isLoading}
                className="absolute right-3 p-2 bg-brand-green/20 text-brand-green rounded-xl hover:bg-brand-green hover:text-bg-dark transition-all disabled:opacity-50"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </section>

        {/* Sidebar Section */}
        <aside className="w-96 glass-morphism flex flex-col border-white/10 shadow-2xl overflow-hidden">
          {/* Tabs */}
          <div className="flex items-center border-b border-white/5">
            {[
              { id: 'roadmap', icon: <Layout size={14} />, label: 'Roadmap' },
              { id: 'explorer', icon: <Search size={14} />, label: 'Explorer' },
              { id: 'health', icon: <BookOpen size={14} />, label: 'Knowledge' }
            ].map(tab => (
              <button 
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-4 text-xs font-bold tracking-wide transition-all ${
                  activeTab === tab.id ? 'text-brand-green border-b-2 border-brand-green bg-brand-green/5' : 'text-white/30 hover:text-white/60'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 p-6 overflow-y-auto custom-scrollbar flex flex-col gap-6">
            {activeTab === 'roadmap' && (
              <>
                <div className="flex items-center justify-between">
                  <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-white/40">Project Synthesis</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-brand-green/10 text-brand-green border border-brand-green/20 font-bold">42% Complete</span>
                </div>
                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-white/30 uppercase tracking-widest">
                    <ChevronRight size={12} className="text-brand-green" /> Phase 1: Hybrid Core
                  </div>
                  <div className="flex flex-col">
                    <SidebarItem title="Neural RAG Engine" description="Local ChromaDB with 50k repo vectors." completed={true} />
                    <SidebarItem title="Cloud Inference Bridge" description="Lightning AI GPU Peer Connection." completed={true} />
                  </div>
                </div>
                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-white/30 uppercase tracking-widest">
                    <ChevronRight size={12} className="text-white/20" /> Phase 2: Refinement
                  </div>
                  <div className="flex flex-col opacity-50">
                    <SidebarItem title="LoRA Adapter V2" description="Fine-tune on latest industry datasets." completed={false} />
                    <SidebarItem title="Discovery Dashboard" description="Visual trends and repo analytics." completed={false} />
                  </div>
                </div>
              </>
            )}

            {activeTab === 'explorer' && (
              <>
                <div className="flex items-center justify-between">
                  <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-white/40">Domain Explorer</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-brand-blue/10 text-brand-blue border border-brand-blue/20 font-bold">50k Repos</span>
                </div>
                {[
                  { label: 'AI / ML', hint: 'LLM, RAG, Transformers, MLOps' },
                  { label: 'Backend', hint: 'FastAPI, gRPC, Microservices' },
                  { label: 'Frontend', hint: 'React, Next.js, GSAP, WebGL' },
                  { label: 'DevOps', hint: 'Kubernetes, Terraform, Helm' },
                  { label: 'Security', hint: 'SAST, ZK, Penetration Testing' },
                  { label: 'Systems', hint: 'Rust, eBPF, WASM, Compilers' },
                  { label: 'Databases', hint: 'Vector DB, DuckDB, ClickHouse' },
                  { label: 'Mobile', hint: 'Flutter, React Native, SwiftUI' },
                ].map(({ label, hint }) => (
                  <div key={label} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/[0.02] px-2 rounded-lg transition-colors group">
                    <span className="text-xs font-bold text-white/60 group-hover:text-white transition-colors">{label}</span>
                    <span className="text-[10px] text-white/30 font-mono">{hint}</span>
                  </div>
                ))}
              </>
            )}

            {activeTab === 'health' && (
              <>
                <div className="flex items-center justify-between">
                  <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-white/40">Model Knowledge</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-brand-green/10 text-brand-green border border-brand-green/20 font-bold">Active</span>
                </div>
                {[
                  { label: 'Base Model', value: 'Llama-3-8B-Instruct' },
                  { label: 'Quantization', value: '4-bit (MLX)' },
                  { label: 'Fine-tuning', value: 'LoRA Adapters' },
                  { label: 'Training Pairs', value: '50,000+ repos' },
                  { label: 'Max Tokens', value: '600' },
                  { label: 'Inference', value: 'Local (M-series)' },
                ].map(({ label, value }) => (
                  <div key={label} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 px-2">
                    <span className="text-[10px] text-white/40 font-mono uppercase tracking-wider">{label}</span>
                    <span className="text-[10px] font-bold text-white/70">{value}</span>
                  </div>
                ))}
              </>
            )}

          </div>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-white/5 bg-black/20 flex items-center justify-between text-white/30">
            <span className="text-[8px] font-mono uppercase tracking-widest">Status: Synchronized</span>
            <button className="flex items-center gap-1.5 text-[8px] font-bold uppercase transition-colors hover:text-white">
              <Database size={10} /> Export Full Spec
            </button>
          </div>
        </aside>

      </main>

      {/* Global Status Bar */}
      <footer className="w-full max-w-7xl mt-4 px-4 flex items-center justify-between text-[10px] font-mono text-white/20">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-brand-green" /> Hybrid Bridge: Online</span>
          <span className="flex items-center gap-1.5">Cloud Expert (Llama-3): <span className="text-white/40">Active</span></span>
        </div>
        <div className="flex items-center gap-4 hover:text-white/40 cursor-pointer transition-colors">
          <Github size={12} /> github.com/piyushdua/repohunter
        </div>
      </footer>
    </div>
  );
}
