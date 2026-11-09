"""Internal evidence bookkeeping; public findings keep their existing JSON shape."""
from dataclasses import dataclass, field

LAYERS = ('structure_export', 'geometry', 'scientific', 'readability', 'publication')


class Findings:
    """Collect findings once, with explicit ownership at each validation call site."""

    def __init__(self, *, parent=None, layers=('structure_export', 'publication')):
        self.items = parent.items if parent is not None else []
        self.by_layer = parent.by_layer if parent is not None else {name: [] for name in LAYERS}
        self.layers = layers

    def for_layers(self, *layers):
        return Findings(parent=self, layers=layers)

    def append(self, finding):
        self.items.append(finding)
        for layer in self.layers:
            self.by_layer[layer].append(finding)

    def extend(self, findings):
        for finding in findings:
            self.append(finding)

    def __iter__(self):
        return iter(self.items)


@dataclass
class CheckExecution:
    executed: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)

    @property
    def complete(self):
        return bool(self.executed) and not self.blocked


@dataclass
class ManifestEvaluation:
    validation: dict
    findings_by_layer: dict
    checks: dict[str, CheckExecution]
