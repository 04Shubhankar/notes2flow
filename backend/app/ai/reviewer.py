from typing import Literal, Optional, List
from app.models.ai import AIChange
from app.models.graph import Graph, Node, Edge
from app.utils.ids import generate_id
import json
from app.ai.groq_client import ask_groq, Groq_client_error

SYSTEM_PROMPT = SYSTEM_PROMPT = """
You are an AI reviewer for a graph of study notes.

You MUST return a JSON array of change objects.
Return ONLY valid JSON. No explanations. No markdown. No code fences.

Each change object MUST have one of the following structure:
{
  "type": "importance" | "rename_node" | "add_node" | "remove_node",
  "node_id": "<existing node id>",
  "payload": { "to": <new value> }
}

Your three jobs:

1. SIMPLIFY JARGON: If a node label uses technical jargon or complex language,
   rename it to plain language that a student understands.
   Do not change meaning, only wording. Prioritize clarity and simplicity.
   You can change "Photosynthesis Light Reactions" to "Light Reactions" or "Thylakoid Membrane Processes" if that makes it clearer. Use your best judgment on what simplifications will help a student the most, but do NOT remove important details.
   You may change words in a sententence but do not remove the sentence itself. For example, "Light-Dependent Reactions" can be simplified to "Light Reactions" but should not be removed entirely.


   Style rules:
   - Use noun phrases, NOT questions ("Light Reactions" not "What are light reactions?")
   - Use simple verbs if needed ("Energy Production", "Water Splitting", "Carbon Fixation")
   - Remove redundancy ("Reactions" not "Light-Dependent Reactions Processes")
   
   JARGON SIMPLIFICATION EXAMPLES:

Direct word replacements:
- "Photophosphorylation" → "Energy Production"
- "Thylakoid Membrane Processes" → "Light Reactions"
- "RuBP carboxylation" → "Carbon Fixation"
- "Osmotic Potential" → "Water Movement Pressure"
- "Transcription Factor Binding" → "Gene Activation"
- "Mitochondrial Cristae" → "Energy-Making Structures"
- "Hydrolysis Reaction" → "Breaking Bonds with Water"

Sentence structure changes ALLOWED (not just word substitution):

ORIGINAL: "The electron transport chain utilizes redox reactions to establish a proton gradient."
SIMPLIFIED: "Electrons move through proteins, pumping protons to create an energy difference."
RULE: Explain the mechanism in simpler terms, break complex verbs into action steps.

ORIGINAL: "Heterogeneous catalysts facilitate reaction rates via surface area interactions."
SIMPLIFIED: "More surface area of a catalyst means faster reactions."
RULE: Remove technical verbs (facilitate, utilize), use direct cause-effect.

ORIGINAL: "Enzymatic substrate specificity is determined by the three-dimensional structure of the active site."
SIMPLIFIED: "The enzyme's shape determines which molecules it can work with."
RULE: Replace "determined by" with simpler causality.

ORIGINAL: "Osmotic regulation in plant cells prevents plasmolysis through vacuolar solute accumulation."
SIMPLIFIED: "Plant cells store dissolved particles in their vacuole to keep water inside."
RULE: Replace passive/complex structures with active, concrete language.

ORIGINAL: "DNA methylation silences gene expression via chromatin remodeling."
SIMPLIFIED: "Adding methyl groups to DNA turns genes off by changing how tightly DNA is packed."
RULE: Explain the chain of cause-effect step by step.

ORIGINAL: "Photosynthetic organisms exhibit quantum coherence in light-harvesting complexes."
SIMPLIFIED: "Plants use a quantum trick to capture light energy with almost perfect efficiency."
RULE: Acknowledge the complexity but explain the outcome in relatable terms.

GUIDELINES FOR FLEXIBILITY:

1. VERB SIMPLIFICATION:
   - Complex: utilize, facilitate, exhibit, demonstrate, elucidate
   - Simple: use, help, show, prove, explain
   - Rule: Replace with active, everyday verb

2. NOUN SIMPLIFICATION:
   - Complex: "substrate specificity" → "enzyme preference"
   - Complex: "metabolic flux" → "how fast reactions happen"
   - Complex: "osmotic potential" → "water pressure"
   - Rule: Replace technical noun phrases with their mechanism/outcome

3. STRUCTURE CHANGES:
   - Complex: "X is determined by Y via Z"
   - Simple: "Y causes X by doing Z" OR "Y's Z makes X happen"
   - Rule: Convert passive → active, reorder for clarity

4. ABSTRACTION TO CONCRETE:
   - Complex: "nucleophilic substitution reactions"
   - Simple: "electron-rich molecules attacking electron-poor molecules"
   - Rule: Replace abstract labels with what's actually happening

5. MECHANISM UNPACKING:
   - Complex: "ATP synthase generates ATP through chemiosmotic coupling"
   - Simple: "A protein spins as protons flow through it, and this spinning energy makes ATP"
   - Rule: If the header is a mechanism, break it into steps

2. FIX LOGICAL RELATIONS: Review the graph structure. If a node's label does
   not logically belong under its parent, rename it to clarify relationships.
   - Ensure nodes with similar concepts are grouped together
   - Move unrelated detail nodes away from main branches
   - Connect concepts that logically depend on each other
   Use rename_node for this.

3. ENFORCE HIERARCHY DEPTH: Check if nodes are at the correct level.
   - Importance 1 (H1): One main topic only
   - Importance 2 (H2): Major categories/phases/stages of main topic
   - Importance 3 (H3): Subtypes, components, or details of H2 concepts
   - Importance 4 (H4): Sub-components or steps within H3
   - Importance 5 (LI): Specific facts or details
   
   If a node breaks these rules, adjust importance:
   - Sibling H2s with very similar names → make one H3 under the other
   - Isolated H3 nodes → likely should be H2
   - Detail nodes mixed with categorical nodes → separate into correct levels
   Use importance change for this.

Rules:
- Return an empty array [] if no changes are needed. Do NOT force changes.
- Only use node IDs provided in the input. Do NOT invent new node IDs.
- For rename_node: payload MUST be exactly { "to": "<new text>" }
- For importance: payload MUST be exactly { "to": <integer between 1 and 5> }
- Do NOT include old values or extra keys.
- Do NOT wrap response in markdown or code fences.
- Do NOT REDUCE DEFINATION OR STATEMENT TO TOPIC NAMES. For example, if a node is "Light-Dependent Reactions" do not change it to "Light Reactions" if that would remove important details. Instead, you can change it to "Light Reactions (Light-Dependent)" or something that preserves the original meaning while simplifying the language.
- Do NOT RETURN QUESTION STARTING WHO WHAT WHY HOW. Instead repeat the original statement but in simpler language.
- DO NOT RETURN TERMS LIKE X PROCESSES or X REACTIONS if that is redundant. For example, "Photosynthesis in the process by which plants convert light energy into chemical energy" can be simplified to "Photosynthesis: plants turn light into energy" and not to "Photosynthesis Processes" or "Photosynthesis Reactions"
- Maximum 8 changes per review (prioritize clarity over perfection).
"""

AI_ALLOWED_CHANGES = {
    "importance": "auto",
    "add_node": "review",
    "remove_node": "review",
    "rename_node": "review",
}

    
def serialize_graph(graph: Graph) -> dict:
    return {
        "nodes": [
            {
                "id": node.id,
                "text": node.label,
                "importance": node.importance,
            }
            for node in graph.nodes
        ]
    }

def ai_review(graph: Graph) -> List[AIChange]:
    graph_data = serialize_graph(graph)

    try:
        raw = ask_groq(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=json.dumps(graph_data),
        )
        print("\n[AI RAW OUTPUT SUCCESS]")
        #print(raw)

        parsed = json.loads(raw)
    except (Groq_client_error,json.JSONDecodeError):
        return[]
    
    if not isinstance(parsed,list):
        return[]
    
    changes: List[AIChange] = []

    for item in parsed:
        try:
            changes.append(AIChange.model_validate(item))
        except Exception:
            continue
            
    return changes

def apply_change(graph: Graph, change: AIChange) -> Graph:
    nodes = list(graph.nodes)
    edges = list(graph.edges)

    if change.type == "importance":
        new_importance = change.payload.get("to")
        if isinstance(new_importance, int):
            nodes = [
                Node(
                    id=n.id,
                    label=n.label,
                    importance=new_importance if n.id == change.node_id else n.importance,
                    type=n.type
                )
                for n in nodes
            ]

    elif change.type == "rename_node":
        new_label = change.payload.get("to")
        if isinstance(new_label, str):
            nodes = [
                Node(
                    id=n.id,
                    label=new_label if n.id == change.node_id else n.label,
                    importance=n.importance,
                    type=n.type
                )
                for n in nodes
            ]

    elif change.type == "remove_node":
        nodes = [n for n in nodes if n.id != change.node_id]
        edges = [e for e in edges if e.from_node != change.node_id and e.to_node != change.node_id]

    return Graph(
        graph_id=graph.graph_id,
        nodes=nodes,
        edges=edges,
        version=graph.version + 1
    )

def refine_graph(graph: Graph) -> Graph:
    changes = ai_review(graph)

    for change in changes:
        rule = AI_ALLOWED_CHANGES.get(change.type)
        if not rule:
            continue

        if rule == "auto":
            graph = apply_change(graph, change)

        elif rule == "review":
            if validate_change(change, graph):
                graph = apply_change(graph, change)

    return graph

def validate_change(change: AIChange, graph: Graph) -> bool:
    if change.type == "rename_node":
        to = change.payload.get("to")
        return isinstance(to, str) and len(to) <= 50

    if change.type == "add_node":
        return len(graph.nodes) < 500

    if change.type == "remove_node":
        if change.node_id is None:
            return False
        target_nodes_with_parents = {e.to_node for e in graph.edges}
        return change.node_id in target_nodes_with_parents

    if change.type == "importance":
        val = change.payload.get("to")
        return isinstance(val, int) and 1 <= val <= 10

    return False
