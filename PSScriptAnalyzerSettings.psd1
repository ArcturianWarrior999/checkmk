# PSScriptAnalyzer reference (settings file syntax, rule suppression, running locally):
# https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules
@{
    # ParseError is a distinct DiagnosticSeverity value from Error in
    # PSScriptAnalyzer, not a subset of it, so it must be listed explicitly
    # or genuine syntax errors pass the lint silently.
    Severity = @('Error', 'ParseError')
}
