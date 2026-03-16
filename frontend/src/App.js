import { useEffect, useState, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import {
  VolumeX,
  Volume2,
  LogOut,
  Ban,
  ShieldPlus,
  ShieldMinus,
  Smile,
  Crown,
  HelpCircle,
  Terminal,
  Clock,
  Zap,
  Users,
  Activity,
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ── helpers ─────────────────────────────────────── */
function formatUptime(seconds) {
  if (!seconds || seconds <= 0) return "0s";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const parts = [];
  if (d) parts.push(`${d}d`);
  if (h) parts.push(`${h}h`);
  if (m) parts.push(`${m}m`);
  return parts.join(" ") || "< 1m";
}

/* ── static command data ────────────────────────── */
const COMMAND_SECTIONS = [
  {
    id: "mute",
    title: "Mute Commands",
    icon: VolumeX,
    note: "Default 1h. Add time: 10m, 2h, 3d, 1w, 2mo, 1y",
    commands: [
      { cmd: "/shutup", desc: "Shut your stinking mouth" },
      { cmd: "/shush", desc: "Stop Yappin" },
      { cmd: "/ftg", desc: "Ferme ta gueule big" },
      { cmd: "/bec", desc: "Aie bec!" },
      { cmd: "/stopbarking", desc: "Stop barking, Bitch" },
      { cmd: "/artdejapper", desc: "Arrete d'aboyer pti chiwawa" },
      { cmd: "/sybau", desc: "Shut your bitch AHHHH up" },
      { cmd: "/goofy", desc: "You're gay, can't talk faggot" },
      { cmd: "/keh", desc: "Ferme ta jgole senti ptite sharmouta" },
      { cmd: "/vio", desc: "PERMANENT mute", permanent: true },
    ],
  },
  {
    id: "unmute",
    title: "Unmute Commands",
    icon: Volume2,
    commands: [
      { cmd: "/talk", desc: "Talk respectfully n*gga" },
      { cmd: "/parle", desc: "Parle bien bruv" },
    ],
  },
  {
    id: "kick",
    title: "Kick Commands",
    icon: LogOut,
    commands: [
      { cmd: "/sort", desc: "Trace ta route bouzin senti" },
      { cmd: "/getout", desc: "Go take a bath" },
      { cmd: "/decawlis", desc: "Ta yeule pu la marde" },
    ],
  },
  {
    id: "ban",
    title: "Ban Commands",
    icon: Ban,
    commands: [
      { cmd: "/ntm", desc: "Vazi niquer ta marrain" },
      { cmd: "/bouge", desc: "Ayo bouge tu parle trop" },
      { cmd: "/ciao", desc: "Ciao per sempre" },
    ],
  },
  {
    id: "admin",
    title: "Admin Commands",
    icon: ShieldPlus,
    commands: [
      { cmd: "/levelup", desc: "Promote to Casper's VIP" },
      { cmd: "/debout", desc: "Promote to Casper's VIP" },
      { cmd: "/assistoi", desc: "Demote \u2014 mauvais chien" },
      { cmd: "/leveldown", desc: "Remove VIP status" },
    ],
  },
  {
    id: "fun",
    title: "Fun Commands",
    icon: Smile,
    note: "No punishment applied",
    commands: [
      { cmd: "/pussy", desc: "You're acting scared" },
      { cmd: "/shifta", desc: "Go do your shift" },
      { cmd: "/cap", desc: "Stop the cap / T'es un mytho" },
      { cmd: "/mgd", desc: "MTL Groups Destroyed" },
      { cmd: "/fu", desc: "..." },
      { cmd: "/gay", desc: "You're a faggot" },
    ],
  },
  {
    id: "owner",
    title: "Owner Mention",
    icon: Crown,
    commands: [
      {
        cmd: "/papa /pere /boss /patron /chef /owner /roi /king",
        desc: "Mention the owner @casperthe6ix",
      },
    ],
  },
  {
    id: "help",
    title: "Help",
    icon: HelpCircle,
    commands: [
      { cmd: "/help", desc: "Get command list in DMs (group) or inline (private)" },
    ],
  },
];

/* ── Stat Card ──────────────────────────────────── */
function StatCard({ icon: Icon, label, value, testId }) {
  return (
    <div className="stat-card" data-testid={testId}>
      <div className="stat-icon">
        <Icon size={18} />
      </div>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
    </div>
  );
}

/* ── Command Row ────────────────────────────────── */
function CommandRow({ cmd, desc, permanent }) {
  return (
    <div className="cmd-row" data-testid={`cmd-${cmd.replace(/\s/g, "-").replace(/\//g, "")}`}>
      <code className="cmd-name">{cmd}</code>
      <span className="cmd-desc">{desc}</span>
      {permanent && (
        <Badge variant="destructive" className="cmd-badge">
          PERMANENT
        </Badge>
      )}
    </div>
  );
}

/* ── Main App ───────────────────────────────────── */
export default function App() {
  const [status, setStatus] = useState({ status: "offline", uptime_seconds: 0 });
  const [stats, setStats] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [statusRes, statsRes] = await Promise.all([
        axios.get(`${API}/bot/status`),
        axios.get(`${API}/bot/stats`),
      ]);
      setStatus(statusRes.data);
      setStats(statsRes.data);
    } catch {
      setStatus((s) => ({ ...s, status: "offline" }));
    }
  }, []);

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 30000);
    return () => clearInterval(id);
  }, [fetchData]);

  const online = status.status === "online";

  return (
    <div className="app-root">
      {/* scanline overlay */}
      <div className="scanline-overlay" />

      <div className="container">
        {/* ── Header ─────────────────────────── */}
        <header className="header" data-testid="header">
          <div className="header-left">
            <Terminal size={22} className="header-icon" />
            <h1 className="header-title">
              CASPER<span className="accent">MOD</span>BOT
            </h1>
          </div>
          <div className="header-right">
            <div
              className={`status-dot ${online ? "online" : "offline"}`}
              data-testid="status-indicator"
            />
            <Badge
              variant={online ? "default" : "secondary"}
              className={`status-badge ${online ? "badge-online" : "badge-offline"}`}
              data-testid="status-badge"
            >
              {online ? "ONLINE" : "OFFLINE"}
            </Badge>
          </div>
        </header>

        {/* ── Stats Grid ─────────────────────── */}
        <section className="stats-grid" data-testid="stats-grid">
          <StatCard
            icon={Clock}
            label="Uptime"
            value={online ? formatUptime(status.uptime_seconds) : "--"}
            testId="stat-uptime"
          />
          <StatCard
            icon={Zap}
            label="Commands"
            value={stats ? stats.total_commands : "--"}
            testId="stat-commands"
          />
          <StatCard
            icon={Users}
            label="Groups"
            value={stats ? stats.groups_count : "--"}
            testId="stat-groups"
          />
          <StatCard
            icon={Activity}
            label="Version"
            value="1.0.0"
            testId="stat-version"
          />
        </section>

        {/* ── Commands ───────────────────────── */}
        <section className="commands-section" data-testid="commands-section">
          <h2 className="section-title">
            <span className="accent">//</span> SYSTEM COMMANDS
          </h2>

          <Accordion type="multiple" className="accordion-root">
            {COMMAND_SECTIONS.map((section) => {
              const Icon = section.icon;
              return (
                <AccordionItem
                  key={section.id}
                  value={section.id}
                  className="accordion-item"
                  data-testid={`section-${section.id}`}
                >
                  <AccordionTrigger className="accordion-trigger">
                    <span className="trigger-content">
                      <Icon size={16} className="trigger-icon" />
                      {section.title}
                      {section.note && (
                        <span className="trigger-note">{section.note}</span>
                      )}
                    </span>
                  </AccordionTrigger>
                  <AccordionContent className="accordion-content">
                    {section.commands.map((c, i) => (
                      <CommandRow key={i} {...c} />
                    ))}
                  </AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </section>

        {/* ── Footer ─────────────────────────── */}
        <footer className="footer" data-testid="footer">
          <span className="footer-dot" />
          System {online ? "Online" : "Offline"} &middot; v1.0.0 &middot;
          owner @casperthe6ix
        </footer>
      </div>
    </div>
  );
}
