// A notice that stays until it is dismissed, and then stays away on every device: the
// server is told (static/js/seen.js). Used for a new version of the educator kit
// (desk/templates/desk/educators.html).

import { report } from "../seen.js";

export default () => ({
  gone: false,
  dismiss() {
    report("kit", this.$root);
    this.gone = true;
  },
});
