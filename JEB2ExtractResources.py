"""
extract apk's resource files
"""

import os
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import IBinaryUnit, IXmlUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from jarray import array, zeros

class JEB2ExtractResources(IScript):

  def run(self, ctx):
    self.ctx = ctx

    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    prj = projects[0]
    print('=> Listing units int project "%s":' % prj.getName())
    prjname = prj.getName()
    outdir = os.path.join(prjname[:prjname.rfind('/') + 1], 'resources')
    print('=> outdir "%s":' % outdir)

    for art in prj.getLiveArtifacts():
      for unit in art.getUnits():
        self.checkUnit(unit, outdir)

    print('---- extracted over ----');

  def getTextDocument(self, srcUnit):
    formatter = srcUnit.getFormatter()
    if formatter and formatter.getDocumentPresentations():
      doc = formatter.getDocumentPresentations()[0].getDocument()
      if isinstance(doc, ITextDocument):
        return doc
    return None

  def formatTextDocument(self, doc):
    s = ''
    # retrieve the entire document -it's a source file,
    # no need to buffer individual parts. 10 MLoC is enough 
    alldoc = doc.getDocumentPart(0, 10000000)
    for line in alldoc.getLines():
      s += line.getText().toString() + '\n'
    return s

  def checkUnit(self, unit, outdir, level=0):
    unitsize = -1
    if isinstance(unit, IBinaryUnit):
      unitinput = unit.getInput()
      # use the input
      # ...
      unitsize = unitinput.getCurrentSize()


    s = '  ' * level + unit.getName()
    filepath = ""
    if unitsize >= 0:
      s += ' (%d bytes)' % unitsize
      if isinstance(unit, IXmlUnit):
        doc = self.getTextDocument(unit)
        if not doc:
          print('The source text document was not found')
          return

        text = self.formatTextDocument(doc)
        filepath = os.path.join(outdir, unit.getName())
        f = open(filepath, 'w')
        f.write(text.encode('utf-8'))
        f.close()
        #print("-> %s" %filepath)
      elif not unit.getChildren():
        filepath = os.path.join(outdir, unit.getName())
        print("-> %s : %d bytes" %(filepath, unitsize))
        srcfile = unitinput.getStream()
        length = srcfile.available();
        buff = zeros(length, 'b')
        f = open(filepath, 'wb')
        srcfile.read(buff)
        f.write(buff)
        f.close()

    #print(s)

    # recurse over children units
    if unit.getChildren():
      nextdir = os.path.join(outdir, unit.getName())
      if not os.path.exists(nextdir):
        os.makedirs(nextdir)

      for c in unit.getChildren():
        self.checkUnit(c, nextdir, level + 1)
