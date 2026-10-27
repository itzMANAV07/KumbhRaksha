import React from "react";

export interface ProcessStep {
  id: string;
  num: string;
  title: string;
  subtitle: string;
  status: "completed" | "active" | "standby";
}

interface ProcessStepperProps {
  activeStep?: string;
  onStepClick?: (stepId: string) => void;
}

export const ProcessStepper: React.FC<ProcessStepperProps> = ({
  activeStep = "predict",
  onStepClick,
}) => {
  const steps: ProcessStep[] = [
    {
      id: "sense",
      num: "01",
      title: "Edge Sensing",
      subtitle: "GeoJSON Polygons & Counts",
      status: "completed",
    },
    {
      id: "predict",
      num: "02",
      title: "30m Forecast",
      subtitle: "Rate Gradient dp/dt",
      status: activeStep === "predict" ? "active" : "completed",
    },
    {
      id: "divert",
      num: "03",
      title: "Corridor Divert",
      subtitle: "Lowest Adjacent Density",
      status: activeStep === "divert" ? "active" : "standby",
    },
    {
      id: "dispatch",
      num: "04",
      title: "Multilingual Dispatch",
      subtitle: "Telegram & Webhook Alerts",
      status: activeStep === "dispatch" ? "active" : "standby",
    },
    {
      id: "reunite",
      num: "05",
      title: "Explainable Match",
      subtitle: "Biometric-Free Reunification",
      status: activeStep === "reunite" ? "active" : "standby",
    },
  ];

  return (
    <div className="process-stepper-wrap" role="region" aria-label="Crowd Safety Pipeline">
      <div className="process-stepper-line-track">
        <div className="process-stepper-beam" />
      </div>

      <div className="process-stepper-items">
        {steps.map((step) => {
          const isActive = step.id === activeStep;
          return (
            <button
              key={step.id}
              className={`process-step-node ${isActive ? "process-step-node--active" : ""}`}
              onClick={() => onStepClick?.(step.id)}
              type="button"
              id={`step-${step.id}`}
            >
              <div className="process-step-badge">
                <span className="process-step-num">{step.num}</span>
                <span className="process-step-pulse" />
              </div>
              <div className="process-step-info">
                <span className="process-step-title">{step.title}</span>
                <span className="process-step-sub">{step.subtitle}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
