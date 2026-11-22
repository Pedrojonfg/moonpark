import { Button, Collapse, FormGroup, Slider, Switch } from "@blueprintjs/core";
import { useCallback, useEffect, useState } from "react";
import { apiUrl } from "./api";

type SessionMemory = {
  installed_ram_mb: number;
  pcp_cache_budget_mb: number;
  session_budget_mb: number;
  pcp_ram_fraction_default: number;
  session_ram_fraction_default: number;
  pcp_xy_high_precision: boolean;
  overrides: Record<string, unknown>;
};

export function EngineMemoryPanel() {
  const [open, setOpen] = useState(false);
  const [cfg, setCfg] = useState<SessionMemory | null>(null);
  const [pcpPct, setPcpPct] = useState(20);
  const [sessPct, setSessPct] = useState(50);
  const [highPrec, setHighPrec] = useState(false);

  const load = useCallback(async () => {
    const res = await fetch(apiUrl("/session-memory"));
    if (!res.ok) return;
    const j = (await res.json()) as SessionMemory;
    setCfg(j);
    const po = j.overrides?.pcp_ram_fraction;
    setPcpPct(typeof po === "number" ? po * 100 : j.pcp_ram_fraction_default * 100);
    const so = j.overrides?.session_ram_fraction;
    setSessPct(typeof so === "number" ? so * 100 : j.session_ram_fraction_default * 100);
    setHighPrec(Boolean(j.overrides?.pcp_xy_high_precision ?? j.pcp_xy_high_precision));
  }, []);

  useEffect(() => {
    if (open) void load();
  }, [open, load]);

  const apply = async (reset = false) => {
    await fetch(apiUrl("/session-memory"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        reset
          ? { reset_automatic: true }
          : {
              pcp_ram_fraction: pcpPct / 100,
              session_ram_fraction: sessPct / 100,
              pcp_xy_high_precision: highPrec,
            },
      ),
    });
    await load();
  };

  return (
    <div style={{ marginTop: 8 }}>
      <Button minimal small onClick={() => setOpen((v) => !v)}>
        Engine memory…
      </Button>
      <Collapse isOpen={open}>
        {cfg && (
          <div style={{ padding: "8px 0", maxWidth: 420 }}>
            <FormGroup label={`PCP cache (~${cfg.pcp_cache_budget_mb} MB of ${cfg.installed_ram_mb} MB RAM)`}>
              <Slider min={5} max={50} stepSize={1} labelStepSize={10} onChange={setPcpPct} value={pcpPct} />
            </FormGroup>
            <FormGroup label={`Session budget (~${cfg.session_budget_mb} MB)`}>
              <Slider min={20} max={80} stepSize={1} labelStepSize={20} onChange={setSessPct} value={sessPct} />
            </FormGroup>
            <Switch
              checked={highPrec}
              label="High precision PCP coordinates (float64)"
              onChange={() => setHighPrec((v) => !v)}
            />
            <Button small intent="primary" onClick={() => void apply()}>
              Apply
            </Button>{" "}
            <Button small onClick={() => void apply(true)}>
              Reset to automatic
            </Button>
          </div>
        )}
      </Collapse>
    </div>
  );
}