package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2017, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistXfmrTank extends DistComponent {
	public String id;
	public String pname;
	public String vgrp;
	public String tname;
	public String tankinfo;
	public String infoid;
	public String[] bus;
	public String[] phs;
	public String[] ename;
	public String[] eid;
	public double[] basev;
	public double[] rg;
	public double[] xg;
	public int[] wdg;
	public boolean[] grounded;

	public double normalCurrentLimit = 0.0;
	public double emergencyCurrentLimit = 0.0;

	public boolean glmUsed;

	public int size;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + pname +"\"");
		buf.append (",\"mRID\":\"" + id +"\"");
		buf.append ("}");
		return buf.toString();
	}

	private void SetSize (int val) {
		size = val;
		bus = new String[size];
		phs = new String[size];
		ename = new String[size];
		eid = new String[size];
		wdg = new int[size];
		grounded = new boolean[size];
		basev = new double[size];
		rg = new double[size];
		xg = new double[size];
	}

	public DistXfmrTank (ResultSet results, HashMap<String,Integer> map) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			pname = SafeName (soln.get("?pname").toString());
			id = soln.get("?id").toString();
			infoid = soln.get("?infoid").toString();
			vgrp = soln.get("?vgrp").toString();
			tname = SafeName (soln.get("?tname").toString());
			tankinfo = SafeName (soln.get("?xfmrcode").toString());
			SetSize (map.get(tname));
			glmUsed = true;
			for (int i = 0; i < size; i++) {
				eid[i] = soln.get("?eid").toString();
				ename[i] = SafeName (soln.get("?ename").toString());
				bus[i] = SafeName (soln.get("?bus").toString());
				basev[i] = Double.parseDouble (soln.get("?basev").toString());
				phs[i] = soln.get("?phs").toString();
				rg[i] = OptionalDouble (soln, "?rground", 0.0);
				xg[i] = OptionalDouble (soln, "?xground", 0.0);
				wdg[i] = Integer.parseInt (soln.get("?enum").toString());
				grounded[i] = Boolean.parseBoolean (soln.get("?grounded").toString());
				if ((i + 1) < size) {
					soln = results.next();
				}
			}
		}		
	}

	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append ("pname=" + pname + " vgrp=" + vgrp + " tname=" + tname + " tankinfo=" + tankinfo);
		for (int i = 0; i < size; i++) {
			buf.append ("\n  " + Integer.toString(wdg[i]) + " bus=" + bus[i] + " basev=" + df4.format(basev[i]) + " phs=" + phs[i]);
			buf.append (" grounded=" + Boolean.toString(grounded[i]) + " rg=" + df4.format(rg[i]) + " xg=" + df4.format(xg[i]));
		}
		return buf.toString();
	}

	public String GetJSONSymbols(HashMap<String,DistCoordinates> map) {
		DistCoordinates pt1 = map.get("PowerTransformer:" + pname + ":1");
		DistCoordinates pt2 = map.get("PowerTransformer:" + pname + ":2");
		String bus1 = bus[0];
		String bus2 = bus[1];
		StringBuilder lbl_phs = new StringBuilder ();
		for (int i = 0; i < phs.length; i++) {
			lbl_phs.append(phs[i]);
		}

		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + pname + "\"");
		buf.append (",\"from\":\"" + bus1 + "\"");
		buf.append (",\"to\":\"" + bus2 + "\"");
		buf.append (",\"phases\":\"" + phs[0] +"\"");
		buf.append (",\"configuration\":\"" + tankinfo + ":" + vgrp + "\"");
		buf.append (",\"x1\":" + Double.toString(pt1.x));
		buf.append (",\"y1\":" + Double.toString(pt1.y));
		buf.append (",\"x2\":" + Double.toString(pt2.x));
		buf.append (",\"y2\":" + Double.toString(pt2.y));
		buf.append ("}");
		return buf.toString();
	}

	public String GetGLM () {
		StringBuilder buf = new StringBuilder ("object transformer {\n");

		buf.append ("  name \"xf_" + pname + "\";\n");
		buf.append ("  from \"" + bus[0] + "\";\n");
		buf.append ("  to \"" + bus[1] + "\";\n");
		if (phs[1].contains("s")) {
			buf.append("  phases " + phs[0] + "S;\n");
		} else {
			buf.append("  phases " + phs[0] + ";\n");
		}
		buf.append ("  configuration \"xcon_" + tankinfo + "\";\n");
		AppendGLMRatings (buf, phs[0], normalCurrentLimit, emergencyCurrentLimit);
		buf.append ("  // vector group " + vgrp + ";\n");
		buf.append("}\n");
		return buf.toString();
	}

	public String GetDSS() {
		StringBuilder buf = new StringBuilder ("new Transformer." + tname + " bank=" + pname + " xfmrcode=" + tankinfo + "\n");

		// winding ratings
		AppendDSSRatings (buf, normalCurrentLimit, emergencyCurrentLimit);
		for (int i = 0; i < size; i++) {
			buf.append("~ wdg=" + Integer.toString(i + 1) + " bus=" + DSSXfmrBusPhases (bus[i], phs[i]) + "\n");
		}
		return buf.toString();
	}

  public static String szCSVHeader = "Name,Wdg1Bus,Phase,Wdg2Bus,Phase,Wdg3Bus,Phase,XfmrCode";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (tname);
    for (int i = 0; i < size; i++) {
      buf.append ("," + bus[i] + "," + CSVPhaseString(phs[i]));
    }
    if (size < 3) buf.append (",,");
    buf.append ("," + tankinfo + "\n");
    return buf.toString();
  }

	public String GetKey() {
		return tname;
	}
}

