package gov.pnnl.gridappsd.cimhub.components;
//	----------------------------------------------------------
//	Copyright (c) 2021, Battelle Memorial Institute
//	All rights reserved.
//	----------------------------------------------------------

import org.apache.jena.query.*;
import java.util.HashMap;

public class DistIEEE1547Used extends DistComponent {
	public String id;
	public String name;
  public boolean enabled;
  public String cat;

  public double acVnom;
  public double acVmin;
  public double acVmax;
  public double sMax;
  public double pMax;
  public double pMaxUnderPF;
  public double pMaxOverPF;
  public double underPF;
  public double overPF;
  public double qMaxInj;
  public double qMaxAbs;
  public double pMaxCharge;
  public double apparentPowerChargeMax;

  public boolean vvEnabled;
  public double vvV1;
  public double vvV2;
  public double vvV3;
  public double vvV4;
  public double vvQ1;
  public double vvQ2;
  public double vvQ3;
  public double vvQ4;
  public double vvRef;
  public boolean vvRefAuto;
  public double vvRefOlrt;
  public double vvOlrt;

  public boolean wvEnabled;
  public double wvP1gen;
  public double wvP2gen;
  public double wvP3gen;
  public double wvP1load;
  public double wvP2load;
  public double wvP3load;
  public double wvQ1gen;
  public double wvQ2gen;
  public double wvQ3gen;
  public double wvQ1load;
  public double wvQ2load;
  public double wvQ3load;

  public boolean pfEnabled;
  public double powerFactor;
  public String pfKind;

  public boolean cqEnabled;
  public double reactivePower;

  public boolean vwEnabled;
  public double vwV1;
  public double vwV2;
  public double vwP1;
  public double vwP2gen;
  public double vwP2load;
  public double vwOlrt;

	public String GetJSONEntry () {
		StringBuilder buf = new StringBuilder ();

		buf.append ("{\"name\":\"" + name +"\"");
		buf.append("}");
		return buf.toString();
	}

	public DistIEEE1547Used (ResultSet results) {
		if (results.hasNext()) {
			QuerySolution soln = results.next();
			name = SafeName (soln.get("?name").toString());
			id = soln.get("?id").toString();
      enabled = Boolean.parseBoolean (soln.get("?enabled").toString());
      cat = soln.get("?cat").toString();

      acVnom = Double.parseDouble (soln.get("?acVnom").toString());
      acVmin = Double.parseDouble (soln.get("?acVmin").toString());
      acVmax = Double.parseDouble (soln.get("?acVmax").toString());
      sMax = Double.parseDouble (soln.get("?sMax").toString());
      pMax = Double.parseDouble (soln.get("?pMax").toString());
      pMaxUnderPF = Double.parseDouble (soln.get("?pMaxUnderPF").toString());
      pMaxOverPF = Double.parseDouble (soln.get("?pMaxOverPF").toString());
      underPF = Double.parseDouble (soln.get("?underPF").toString());
      overPF = Double.parseDouble (soln.get("?overPF").toString());
      qMaxInj = Double.parseDouble (soln.get("?qMaxInj").toString());
      qMaxAbs = Double.parseDouble (soln.get("?qMaxAbs").toString());
      pMaxCharge = Double.parseDouble (soln.get("?pMaxCharge").toString());
      apparentPowerChargeMax = Double.parseDouble (soln.get("?apparentPowerChargeMax").toString());

      vvEnabled = Boolean.parseBoolean (soln.get("?vvEnabled").toString());
      vvV1 = Double.parseDouble (soln.get("?vvV1").toString());
      vvV2 = Double.parseDouble (soln.get("?vvV2").toString());
      vvV3 = Double.parseDouble (soln.get("?vvV3").toString());
      vvV4 = Double.parseDouble (soln.get("?vvV4").toString());
      vvQ1 = Double.parseDouble (soln.get("?vvQ1").toString());
      vvQ2 = Double.parseDouble (soln.get("?vvQ2").toString());
      vvQ3 = Double.parseDouble (soln.get("?vvQ3").toString());
      vvQ4 = Double.parseDouble (soln.get("?vvQ4").toString());
      vvRef = Double.parseDouble (soln.get("?vvRef").toString());
      vvRefAuto = Boolean.parseBoolean (soln.get("?vvRefAuto").toString());
      vvRefOlrt = Double.parseDouble (soln.get("?vvRefOlrt").toString());
      vvOlrt = Double.parseDouble (soln.get("?vvOlrt").toString());

      wvEnabled = Boolean.parseBoolean (soln.get("?wvEnabled").toString());
      wvP1gen = Double.parseDouble (soln.get("?wvP1gen").toString());
      wvP2gen = Double.parseDouble (soln.get("?wvP2gen").toString());
      wvP3gen = Double.parseDouble (soln.get("?wvP3gen").toString());
      wvP1load = Double.parseDouble (soln.get("?wvP1load").toString());
      wvP2load = Double.parseDouble (soln.get("?wvP2load").toString());
      wvP3load = Double.parseDouble (soln.get("?wvP3load").toString());
      wvQ1gen = Double.parseDouble (soln.get("?wvQ1gen").toString());
      wvQ2gen = Double.parseDouble (soln.get("?wvQ2gen").toString());
      wvQ3gen = Double.parseDouble (soln.get("?wvQ3gen").toString());
      wvQ1load = Double.parseDouble (soln.get("?wvQ1load").toString());
      wvQ2load = Double.parseDouble (soln.get("?wvQ2load").toString());
      wvQ3load = Double.parseDouble (soln.get("?wvQ3load").toString());

      pfEnabled = Boolean.parseBoolean (soln.get("?pfEnabled").toString());
      powerFactor = Double.parseDouble (soln.get("?powerFactor").toString());
      pfKind = soln.get("?pfKind").toString();

      cqEnabled = Boolean.parseBoolean (soln.get("?cqEnabled").toString());
      reactivePower = Double.parseDouble (soln.get("?reactivePower").toString());

      vwEnabled = Boolean.parseBoolean (soln.get("?vwEnabled").toString());
      vwV1 = Double.parseDouble (soln.get("?vwV1").toString());
      vwV2 = Double.parseDouble (soln.get("?vwV2").toString());
      vwP1 = Double.parseDouble (soln.get("?vwP1").toString());
      vwP2gen = Double.parseDouble (soln.get("?vwP2gen").toString());
      vwP2load = Double.parseDouble (soln.get("?vwP2load").toString());
      vwOlrt = Double.parseDouble (soln.get("?vwOlrt").toString());
		}		
	}
	
	public String DisplayString() {
		StringBuilder buf = new StringBuilder ("");
		buf.append (name);
		return buf.toString();
	}

	public String GetGLM () {
		StringBuilder buf = new StringBuilder ("object inverter {\n");
		buf.append ("  name \"inv_" + name + "\";\n");
		buf.append("}\n");
		return buf.toString();
	}

	public String GetKey() {
		return name;
	}

	public String GetDSS () {
		StringBuilder buf = new StringBuilder ("new InvControl." + name + " // data \n");
		return buf.toString();
	}

  public static String szCSVHeader = "Name,Enabled,Cat,acVnom,acVmin,acVmax,sMaxpMaxOverPF,overPF,pMaxUnderPF,underPF,qMaxInj,"+
   "qMaxAbs,pMaxCharge,apparentPowerChargeMax,vvEnabled,vvV1,vvV2,vvV3,vvV4,vvQ1,vvQ2,vvQ3,vvQ4,vvRef,vvRefAuto,vvRefOlrt,vvOlrt,"+
   "wvEnabled,wvP1gen,wvP2gen,wvP3gen,wvQ1gen,wvQ2gen,wvQ3gen,wvP1load,wvP2load,wvP3load,wvQ1load,wvQ2load,wvQ3load,"+
   "pfEnabled,powerFactor,pfKind,cqEnabled,reactivePower,vwEnabled,vwV1,vwP1,vwV2,vwP2gen,vwP2load,vwOlrt";

  public String GetCSV () {
    StringBuilder buf = new StringBuilder (name + "," + Boolean.toString(enabled) + "," + cat);

    buf.append ("," + df2.format (acVnom));
    buf.append ("," + df2.format (acVmin));
    buf.append ("," + df2.format (acVmax));
    buf.append ("," + df2.format (sMax));
    buf.append ("," + df2.format (pMax));
    buf.append ("," + df2.format (pMaxUnderPF));
    buf.append ("," + df2.format (pMaxOverPF));
    buf.append ("," + df4.format (underPF));
    buf.append ("," + df4.format (overPF));
    buf.append ("," + df2.format (qMaxInj));
    buf.append ("," + df2.format (qMaxAbs));
    buf.append ("," + df2.format (pMaxCharge));
    buf.append ("," + df2.format (apparentPowerChargeMax));

    buf.append ("," + Boolean.toString (vvEnabled));
    buf.append ("," + df3.format (vvV1));
    buf.append ("," + df3.format (vvV2));
    buf.append ("," + df3.format (vvV3));
    buf.append ("," + df3.format (vvV4));
    buf.append ("," + df3.format (vvQ1));
    buf.append ("," + df3.format (vvQ2));
    buf.append ("," + df3.format (vvQ3));
    buf.append ("," + df3.format (vvQ4));
    buf.append ("," + df3.format (vvRef));
    buf.append ("," + Boolean.toString (vvRefAuto));
    buf.append ("," + df2.format (vvRefOlrt));
    buf.append ("," + df4.format (vvOlrt));

    buf.append ("," + Boolean.toString (wvEnabled));
    buf.append ("," + df3.format (wvP1gen));
    buf.append ("," + df3.format (wvP2gen));
    buf.append ("," + df3.format (wvP3gen));
    buf.append ("," + df3.format (wvP1load));
    buf.append ("," + df3.format (wvP2load));
    buf.append ("," + df3.format (wvP3load));
    buf.append ("," + df3.format (wvQ1gen));
    buf.append ("," + df3.format (wvQ2gen));
    buf.append ("," + df3.format (wvQ3gen));
    buf.append ("," + df3.format (wvQ1load));
    buf.append ("," + df3.format (wvQ2load));
    buf.append ("," + df3.format (wvQ3load));

    buf.append ("," + Boolean.toString (pfEnabled));
    buf.append ("," + df4.format (powerFactor));
    buf.append ("," + pfKind);

    buf.append ("," + Boolean.toString (cqEnabled));
    buf.append ("," + df2.format (reactivePower));

    buf.append ("," + Boolean.toString (vwEnabled));
    buf.append ("," + df3.format (vwV1));
    buf.append ("," + df3.format (vwV2));
    buf.append ("," + df3.format (vwP1));
    buf.append ("," + df3.format (vwP2gen));
    buf.append ("," + df3.format (vwP2load));
    buf.append ("," + df4.format (vwOlrt));

    buf.append("\n");
    return buf.toString();
  }
}
