import { getAiosSymbol } from './aiosSymbolManifest.js';
import './AiosSymbol.css';

export default function AiosSymbol({
  name,
  label,
  size = 'md',
  framed = true,
  className = ''
}) {
  const symbol = getAiosSymbol(name);
  const accessibleLabel = label ?? symbol.label;
  const classes = ['aiosSymbol', `aiosSymbol-${size}`, framed ? 'aiosSymbol-framed' : '', className]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={classes} aria-label={accessibleLabel} role="img">
      <img src={symbol.src} alt="" aria-hidden="true" draggable="false" />
    </span>
  );
}
