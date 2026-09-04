import React from "react";
import { MotionSceneProps } from "../types";
import { StepByStepFlow } from "../templates/StepByStepFlow";
import { AnimatedTitle } from "../templates/AnimatedTitle";
import { ConceptHighlight } from "../templates/ConceptHighlight";
import { Comparison } from "../templates/Comparison";
import { Timeline } from "../templates/Timeline";
import { TextReveal } from "../templates/TextReveal";
import { DiagramBuild } from "../templates/DiagramBuild";

export const MotionScene: React.FC<MotionSceneProps> = (props) => {
  switch (props.template) {
    case "animated_title":
      return <AnimatedTitle {...props} />;
    case "concept_highlight":
      return <ConceptHighlight {...props} />;
    case "comparison":
      return <Comparison {...props} />;
    case "timeline":
      return <Timeline {...props} />;
    case "text_reveal":
      return <TextReveal {...props} />;
    case "diagram_build":
      return <DiagramBuild {...props} />;
    case "step_by_step_flow":
    default:
      return <StepByStepFlow {...props} />;
  }
};
