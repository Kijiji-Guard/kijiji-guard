import { Shield, Terminal, FileCode, CheckCircle2, AlertTriangle, Github, Info, Globe, Lock, Database } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  return (
    <div className="min-h-screen bg-[#E4E3E0] text-[#141414] font-sans selection:bg-[#008751] selection:text-white">
      {/* Header */}
      <header className="border-b border-[#141414] p-6 flex justify-between items-center bg-white">
        <div className="flex items-center gap-3">
          <div className="bg-[#008751] p-2 rounded-lg">
            <Shield className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tighter font-display">Kijiji-Guard</h1>
            <p className="text-[10px] uppercase tracking-widest opacity-50 font-mono">Sovereign Security Architecture</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <a href="#vision" className="hover:text-[#008751] transition-colors">Vision</a>
          <a href="#policies" className="hover:text-[#008751] transition-colors">Policies</a>
          <a href="#cli" className="hover:text-[#008751] transition-colors">CLI</a>
          <button className="bg-[#141414] text-white px-4 py-2 rounded-full text-xs hover:bg-[#008751] transition-all">
            Get Started
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6 py-12 space-y-24">
        {/* Hero Section */}
        <section id="vision" className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            <span className="bg-[#008751]/10 text-[#008751] px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest">
              NDPA 2023 Compliance
            </span>
            <h2 className="text-5xl md:text-7xl font-bold tracking-tighter leading-[0.9]">
              Securing Africa's Next <span className="text-[#008751]">Unicorns</span>
            </h2>
            <p className="text-xl opacity-70 max-w-lg leading-relaxed">
              Without the Dollar-Denominated Security Tax. Kijiji-Guard is an indigenous, open-source framework for the African tech ecosystem.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <div className="flex items-center gap-2 bg-white border border-[#141414]/10 px-4 py-2 rounded-xl shadow-sm">
                <CheckCircle2 className="text-[#008751]" size={18} />
                <span className="text-sm font-medium">March 2026 Audit Ready</span>
              </div>
              <div className="flex items-center gap-2 bg-white border border-[#141414]/10 px-4 py-2 rounded-xl shadow-sm">
                <Globe className="text-blue-600" size={18} />
                <span className="text-sm font-medium">Data Residency (Sec. 41)</span>
              </div>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="bg-[#141414] rounded-3xl p-6 shadow-2xl relative overflow-hidden group"
          >
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#008751] to-emerald-400"></div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-500/20 group-hover:bg-red-500 transition-colors"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/20 group-hover:bg-yellow-500 transition-colors"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/20 group-hover:bg-green-500 transition-colors"></div>
              <span className="ml-2 text-[10px] font-mono text-white/30">kijiji scan sample_startup.tf</span>
            </div>
            <pre className="font-mono text-xs text-white/80 leading-relaxed overflow-x-auto">
              <code>{`
Kijiji-Guard NDPA Compliance Report
ID           NDPA Section           Resource                Status
------------------------------------------------------------------
CKV_NGR_001  Section 41 (Residency) aws_vpc.unicorn_vpc     [green]PASS[/green]
CKV_NGR_002  Section 24 (Retention) aws_s3_bucket.kyc_data  [red]FAIL[/red]
CKV_NGR_003  Section 34 (Encryption) aws_s3_bucket.kyc_data  [red]FAIL[/red]

Compliance Score: 33.33%
Action required: Fix violations before the March 2026 Audit cycle.
              `}</code>
            </pre>
          </motion.div>
        </section>

        {/* Policies Section */}
        <section id="policies" className="space-y-12">
          <div className="text-center space-y-4">
            <h3 className="text-4xl font-bold tracking-tight">Indigenous Policies</h3>
            <p className="opacity-60 max-w-2xl mx-auto">Custom Checkov policies specifically mapped to the legal requirements of the Nigeria Data Protection Act 2023.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <PolicyCard 
              id="CKV_NGR_001"
              title="Data Residency"
              section="Section 41"
              description="Ensures data stays in Africa or Adequate Protection zones to prevent illegal cross-border transfers."
              icon={<Globe className="text-blue-600" />}
            />
            <PolicyCard 
              id="CKV_NGR_002"
              title="Retention Enforcement"
              section="Section 24"
              description="Enforces storage limitation principles via S3 lifecycle rules to prevent indefinite data storage."
              icon={<Database className="text-amber-600" />}
            />
            <PolicyCard 
              id="CKV_NGR_003"
              title="Encryption at Rest"
              section="Section 34"
              description="Mandates high-grade AES256 or KMS encryption for all sensitive PII storage resources."
              icon={<Lock className="text-[#008751]" />}
            />
          </div>
        </section>

        {/* CLI / Code Section */}
        <section id="cli" className="bg-white border border-[#141414]/10 rounded-[2rem] p-8 md:p-12 shadow-sm">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div className="space-y-6">
              <h3 className="text-4xl font-bold tracking-tight">The Kijiji CLI</h3>
              <p className="opacity-70 leading-relaxed">
                Built with <span className="font-bold">Typer</span> and <span className="font-bold">Rich</span>, Kijiji-Guard provides a professional terminal experience for developers and security auditors.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-[#008751] p-1 rounded-full"><CheckCircle2 className="text-white" size={12} /></div>
                  <div>
                    <p className="font-bold text-sm">kijiji init</p>
                    <p className="text-xs opacity-50">Bootstrap your project with NDPA policies.</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-[#008751] p-1 rounded-full"><CheckCircle2 className="text-white" size={12} /></div>
                  <div>
                    <p className="font-bold text-sm">kijiji scan &lt;path&gt;</p>
                    <p className="text-xs opacity-50">Run deep analysis against Terraform infrastructure.</p>
                  </div>
                </li>
              </ul>
            </div>
            <div className="bg-[#141414] rounded-2xl p-6 text-white/90 font-mono text-xs overflow-hidden">
              <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-2">
                <span className="text-white/30">main.py</span>
                <FileCode size={14} className="text-white/30" />
              </div>
              <div className="h-64 overflow-y-auto scrollbar-hide">
                <code>{`
@app.command()
def scan(path: str = typer.Argument(".", help="Path to Terraform files")):
    """
    Scans Terraform files for NDPA 2023 violations.
    """
    console.print(f"[bold]Scanning path: {path}[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Running Security Engine...", total=None)
        
        # Run Checkov via subprocess
        cmd = [
            "checkov",
            "-d", path,
            "--external-checks-dir", "policies",
            "--check", "CKV_NGR",
            "--output", "json"
        ]
        # ... process results ...
                `}</code>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#141414]/10 p-12 bg-white text-center space-y-6">
        <div className="flex justify-center gap-6">
          <Github className="opacity-30 hover:opacity-100 cursor-pointer transition-opacity" />
          <Terminal className="opacity-30 hover:opacity-100 cursor-pointer transition-opacity" />
        </div>
        <p className="text-xs opacity-50 uppercase tracking-widest font-mono">
          Kijiji-Guard: Protecting Africa's Next Unicorn.
        </p>
      </footer>
    </div>
  );
}

function PolicyCard({ id, title, section, description, icon }: { id: string, title: string, section: string, description: string, icon: React.ReactNode }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-white border border-[#141414]/10 p-8 rounded-3xl shadow-sm hover:shadow-xl transition-all group"
    >
      <div className="bg-[#E4E3E0] w-12 h-12 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-[#008751]/10 transition-colors">
        {icon}
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono opacity-40">{id}</span>
          <span className="text-[10px] font-bold text-[#008751] uppercase tracking-widest">{section}</span>
        </div>
        <h4 className="text-xl font-bold tracking-tight">{title}</h4>
        <p className="text-sm opacity-60 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}


